let pyodide = null;
let pythonModulesLoaded = false;

function unindentPythonCode(code) {
  const lines = code.split('\n');
  const nonEmptyLines = lines.filter(line => line.trim().length > 0);
  if (nonEmptyLines.length === 0) return code;
  
  const minIndent = Math.min(...nonEmptyLines.map(line => {
    const match = line.match(/^(\s*)/);
    return match ? match[1].length : 0;
  }));
  
  return lines.map(line => {
    if (line.trim().length === 0) return line;
    return line.substring(minIndent);
  }).join('\n');
}
export async function initializePyodide() {
  if (pyodide) {
    return pyodide;
  }

  pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/",
  });

  await pyodide.loadPackage("micropip");
  
  try {
    await pyodide.runPythonAsync(`
      import micropip
      await micropip.install(['pyodide-http'])
      import pyodide_http
      pyodide_http.patch_all()
    `);
  } catch (error) {
    console.warn("Could not install pyodide-http, continuing without it:", error);
  }
  
  const packageUrl = window.DMV_PACKAGE_URL || null;
  
  if (packageUrl) {
    try {
      await pyodide.runPythonAsync(`
        import micropip
        await micropip.install(['${packageUrl}'])
      `);
      pythonModulesLoaded = true;
      console.log("Python modules loaded from wheel");
    } catch (error) {
      console.warn("Failed to load from wheel, trying bundled modules:", error);
      await loadBundledModules();
    }
  } else {
    // Try bundled modules approach
    await loadBundledModules();
  }

  return pyodide;
}

// ============= LOAD BUNDLED MODULES =============
async function loadBundledModules() {
  // Load Python modules from bundled files or use micropip to install
  // This approach assumes Python source files are available or package is installable
  
  // Check if we should use test PyPI (default to true)
  const useTestPyPI = (typeof window.DMV_USE_TEST_PYPI !== 'undefined') && (window.DMV_USE_TEST_PYPI !== false);
  
  if (useTestPyPI) {
    try {
      const testPypiResponse = await fetch('https://test.pypi.org/pypi/esp-matter-dm-validator/json');
      
      if (!testPypiResponse.ok) {
        throw new Error(`Test PyPI API returned status ${testPypiResponse.status}`);
      }
      
      // Check content type before parsing
      const contentType = testPypiResponse.headers.get('content-type') || '';
      if (!contentType.includes('application/json')) {
        console.warn(`Test PyPI returned unexpected content type: ${contentType}`);
        throw new Error(`Test PyPI returned non-JSON content: ${contentType}`);
      }
      
      const packageInfo = await testPypiResponse.json();
      const latestVersion = packageInfo.info.version;
      
      let wheelUrl = null;
      
      if (packageInfo.urls && packageInfo.urls.length > 0) {
        const wheelFile = packageInfo.urls.find(url => 
          url.packagetype === 'bdist_wheel' && 
          (url.python_version === 'py3' || url.python_version === 'py2.py3' || !url.python_version)
        );
        if (wheelFile && wheelFile.url) {
          wheelUrl = wheelFile.url;
        }
      }
      
      if (!wheelUrl) {
        const packageName = packageInfo.info.name;
        const packageNameUnderscore = packageName.replace(/-/g, '_');
        const firstLetter = packageName.substring(0, 1).toLowerCase();
        
        const possibleUrls = [
          `https://test.pypi.org/packages/py3/${firstLetter}/${packageName}/${packageNameUnderscore}-${latestVersion}-py3-none-any.whl`,
          `https://test.pypi.org/packages/py2.py3/${firstLetter}/${packageName}/${packageNameUnderscore}-${latestVersion}-py2.py3-none-any.whl`,
          `https://test.pypi.org/packages/any/${firstLetter}/${packageName}/${packageNameUnderscore}-${latestVersion}-py3-none-any.whl`
        ];
        
        for (const url of possibleUrls) {
          try {
            const testResponse = await fetch(url, { method: 'HEAD' });
            if (testResponse.ok) {
              wheelUrl = url;
              break;
            }
          } catch (e) {
            continue;
          }
        }
      }
      
      if (!wheelUrl) {
        throw new Error("Could not determine wheel file URL from test PyPI");
      }
      
      await pyodide.runPythonAsync(`
        import micropip
        await micropip.install(['${wheelUrl}'], deps=False)
      `);
      pythonModulesLoaded = true;
      return;
      
    } catch (testPypiError) {
      console.error("Failed to install from test PyPI, falling back:", testPypiError);
    }
  }
  
  try {
    await pyodide.runPythonAsync(`
      import micropip
      await micropip.install(['esp-matter-dm-validator'], deps=False)
    `);
    pythonModulesLoaded = true;
  } catch (pipError) {
    try {
      await pyodide.runPythonAsync(`
        import micropip
        await micropip.install(['esp-matter-dm-validator'], deps=False, index_urls=['https://test.pypi.org/simple/'])
      `);
      pythonModulesLoaded = true;
    } catch (testPipError) {
      throw new Error("Python package not available. Please configure DMV_PACKAGE_URL or ensure package is installable. Error: " + pipError.message);
    }
  }
  const validationDataVersions = ['1.2', '1.3', '1.4', '1.4.1', '1.4.2', '1.5', 'master'];
  
  pyodide.runPython(`
    import os
    import sys
    os.makedirs('/data', exist_ok=True)
  `);

  for (const version of validationDataVersions) {
    try {
      const response = await fetch(`data/validation_data_${version}.json`);
      if (response.ok) {
        const jsonData = await response.text();
        pyodide.FS.writeFile(`/data/validation_data_${version}.json`, jsonData);
      }
    } catch (e) {
      console.warn(`Could not load validation data for version ${version}:`, e);
    }
  }

  try {
    await pyodide.runPythonAsync(`
      import sys
      import os
      import dmv_tool.validators.conformance_checker as cc
      
      original_load = cc.load_chip_validation_data
      def patched_load_chip_validation_data(spec_version):
        import json
        file_path = f"/data/validation_data_{spec_version}.json"
        try:
          with open(file_path, "r") as f:
            return json.load(f)
        except Exception as e:
          print(f"Warning: Could not load {file_path}, trying original method: {e}")
          return original_load(spec_version)
      
      cc.load_chip_validation_data = patched_load_chip_validation_data
      
      if hasattr(cc, 'BASE_DIR'):
        cc.BASE_DIR = '/data'
    `);
  } catch (patchError) {
    console.warn("Could not patch conformance_checker module:", patchError);
  }

  console.log("✅ Bundled modules and data loaded successfully");
}

export async function parseDatamodelLogs(logData) {
  await ensurePyodideReady();
  
  try {
    const escapedLogData = logData
      .replace(/\\/g, '\\\\')
      .replace(/`/g, '\\`')
      .replace(/\${/g, '\\${');
    
    const pythonCode1 = `import json
log_data_str = """${escapedLogData}"""`;
    
    pyodide.runPython(pythonCode1);
    
    const pythonCode2 = `from dmv_tool.parsers.wildcard_logs import parse_datamodel_logs
import json

parsed = parse_datamodel_logs(log_data_str)
json.dumps(parsed)`;
    
    const result = await pyodide.runPythonAsync(pythonCode2);
    return JSON.parse(result);
  } catch (error) {
    console.error("Error parsing logs:", error);
    throw new Error(`Failed to parse logs: ${error.message}`);
  }
}

export async function detectSpecVersion(parsedData) {
  await ensurePyodideReady();
  
  try {
    pyodide.globals.set('parsed_data_json', JSON.stringify(parsedData));
    
    const pythonCode = `from dmv_tool.validators.conformance_checker import detect_spec_version_from_parsed_data
import json

parsed_data = json.loads(parsed_data_json)
version = detect_spec_version_from_parsed_data(parsed_data)
version if version else "master"`;
    
    const result = await pyodide.runPythonAsync(pythonCode);
    
    return result;
  } catch (error) {
    console.error("Error detecting version:", error);
    return null;
  }
}

export async function validateDeviceConformance(parsedData, specVersion) {
  await ensurePyodideReady();
  
  try {
    pyodide.globals.set('parsed_data_json', JSON.stringify(parsedData));
    pyodide.globals.set('spec_version_str', specVersion);
    
    const pythonCode = `from dmv_tool.validators.conformance_checker import validate_device_conformance
import json

parsed_data = json.loads(parsed_data_json)
spec_version = spec_version_str

validation_results = validate_device_conformance(parsed_data, spec_version)
json.dumps(validation_results)`;
    
    const result = await pyodide.runPythonAsync(pythonCode);
    
    return JSON.parse(result);
  } catch (error) {
    console.error("Error validating conformance:", error);
    throw new Error(`Validation failed: ${error.message}`);
  }
}

export async function getSupportedVersions() {
  await ensurePyodideReady();
  
  try {
    const pythonCode = `from dmv_tool.configs.constants import SUPPORTED_SPEC_VERSIONS
import json

json.dumps(list(SUPPORTED_SPEC_VERSIONS))`;
    
    const result = await pyodide.runPythonAsync(pythonCode);
    
    return JSON.parse(result);
  } catch (error) {
    console.error("Error getting supported versions:", error);
    throw new Error("Error getting supported versions: " + error.message);
  }
}

async function ensurePyodideReady() {
  if (!pyodide) {
    await initializePyodide();
  }
  if (!pythonModulesLoaded) {
    throw new Error("Python modules not loaded");
  }
}

let initializationPromise = null;

export function getPyodide() {
  if (!initializationPromise) {
    initializationPromise = initializePyodide();
  }
  return initializationPromise;
}

getPyodide().then(() => {
  const loadingEl = document.getElementById('pyodide-loading');
  const mainContent = document.getElementById('mainContent');
  if (loadingEl) loadingEl.style.display = 'none';
  if (mainContent) mainContent.style.display = 'block';
  
  window.dispatchEvent(new CustomEvent('pyodide-ready'));
}).catch(error => {
  console.error("Failed to initialize Pyodide:", error);
  const loadingEl = document.getElementById('pyodide-loading');
  if (loadingEl) {
    let errorMessage = error.message || 'Unknown error occurred';
    let troubleshootingTips = '';
    
    if (errorMessage.includes('Python package not available')) {
      troubleshootingTips = `
        <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 6px; text-align: left; max-width: 600px; margin-left: auto; margin-right: auto;">
          <h4 style="margin-top: 0; color: #856404;"><i class="fas fa-lightbulb"></i> Troubleshooting Tips:</h4>
          <ul style="margin: 10px 0; padding-left: 20px; color: #856404;">
            <li>Check your internet connection</li>
            <li>Try refreshing the page</li>
            <li>Check browser console for detailed error messages</li>
            <li>If deploying on GitHub Pages, ensure the package is available on PyPI</li>
            <li>For local development, use the Flask server instead: <code>python run_validator.py</code></li>
          </ul>
        </div>
      `;
    }
    
    loadingEl.innerHTML = `
      <div style="text-align: center; color: #d32f2f;">
        <i class="fas fa-exclamation-triangle fa-3x" style="margin-bottom: 20px;"></i>
        <h3>Failed to Load Python Runtime</h3>
        <p style="font-weight: 500;">${errorMessage}</p>
        ${troubleshootingTips}
        <p style="margin-top: 20px;">
          <button onclick="window.location.reload()" class="btn btn-primary" style="padding: 10px 20px; cursor: pointer;">
            <i class="fas fa-redo"></i> Refresh Page
          </button>
        </p>
      </div>
    `;
  }
});

