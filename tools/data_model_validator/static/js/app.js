import {
  initializeDragAndDrop,
  initializeFileUpload,
  initializeUploadNewButton,
} from "./file-upload.js";
import {
  initializeCopyButtons,
  initializeExpandableSections,
  initializeInteractiveElements,
  initializeModal,
} from "./modal.js";
import {
  initializeDataHandling,
  initializePageProtection,
  initializeSessionManagement,
} from "./session-management.js";
import {
  copyToClipboard,
  downloadJSON,
  showCopyFeedback,
  toggleDetailedResults,
} from "./utils.js";
import { initializeValidationFunctionality } from "./validation.js";

let uploadedFile = null;
let parsedData = null;
let validationData = null;

document.addEventListener("DOMContentLoaded", function () {
  window.addEventListener("pyodide-ready", function() {
    initializeSessionManagement();
    initializeFileUpload();
    initializeDragAndDrop();
    initializeValidationFunctionality();
    initializeUploadNewButton();
    initializeDataHandling();
    initializeInteractiveElements();
    initializeExpandableSections();
    initializeModal();
    initializeCopyButtons();
    initializePageProtection();
    loadExistingData();
  });
});


window.copyCommand = function () {
  const command =
    "./chip-tool any read-by-id 0xFFFFFFFF 0xFFFFFFFF <node-id> 0xFFFF > wildcard_logs.txt";

  copyToClipboard(command).then((success) => {
    if (success) {
      showCopyFeedback();
    }
  });
};

window.downloadValidationReport = function () {
  const validationData = localStorage.getItem("currentValidationData");
  if (validationData) {
    downloadJSON(JSON.parse(validationData), "validation_report.json");
  } else {
    alert("No validation data available to download");
  }
};

window.downloadParsedData = function () {
  const parsedData = localStorage.getItem("currentParsedData");
  if (parsedData) {
    downloadJSON(JSON.parse(parsedData), "parsed_data.json");
  } else {
    alert("No parsed data available to download");
  }
};

window.toggleDetailedResults = toggleDetailedResults;

function loadExistingData() {
  const parsedData = localStorage.getItem("currentParsedData");
  const validationData = localStorage.getItem("currentValidationData");
  const uploadedFilename = localStorage.getItem("currentUploadedFilename");
  const detectedVersion = localStorage.getItem("detectedVersion");

  if (parsedData && uploadedFilename) {
    const uploadSection = document.getElementById("uploadSection");
    const uploadSuccessSection = document.getElementById("uploadSuccessSection");
    
    if (uploadSection) uploadSection.style.display = "none";
    if (uploadSuccessSection) uploadSuccessSection.style.display = "block";
    
    const filenameEl = document.getElementById("uploadedFilename");
    if (filenameEl) filenameEl.textContent = uploadedFilename;

    import("./pyodide-bridge.js").then(module => {
      module.getSupportedVersions().then(versions => {
        populateVersionDropdown(versions, detectedVersion);
      });
    });

    if (validationData) {
      import("./results-renderer.js").then(module => {
        module.renderValidationResults(
          JSON.parse(validationData),
          JSON.parse(parsedData)
        );
      });
    }
  }
}

function populateVersionDropdown(versions, detectedVersion) {
  const versionSelect = document.getElementById("complianceVersion");
  if (!versionSelect) return;

  while (versionSelect.options.length > 1) {
    versionSelect.remove(1);
  }

  if (detectedVersion && versions.includes(detectedVersion)) {
    const option = document.createElement("option");
    option.value = detectedVersion;
    option.textContent = `${detectedVersion} (Auto-detected - Recommended)`;
    option.selected = true;
    versionSelect.appendChild(option);
  }

  versions.forEach(version => {
    if (version !== detectedVersion) {
      const option = document.createElement("option");
      option.value = version;
      option.textContent = version;
      versionSelect.appendChild(option);
    }
  });
}

document.addEventListener("keydown", function (e) {
  if ((e.ctrlKey || e.metaKey) && e.key === "u") {
    e.preventDefault();
    const fileInput = document.getElementById("fileInput");
    if (fileInput) {
      fileInput.click();
    }
  }

  if (e.key === "Escape") {
    const modal = document.getElementById("clusterModal");
    if (modal && modal.style.display === "flex") {
      if (window.closeClusterModal) {
        window.closeClusterModal();
      }
    } else {
      const resetUploadArea = document.querySelector(".upload-area");
      if (resetUploadArea && window.resetUploadArea) {
        window.resetUploadArea();
      }
    }
  }
});
