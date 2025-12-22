let sessionId = null;
let heartbeatInterval = null;

export function initializeSessionManagement() {
  sessionId = Date.now() + "_" + Math.random().toString(36).substr(2, 9);

  window.addEventListener("beforeunload", function () {
    sessionCleanup();
  });

  window.addEventListener("pagehide", function () {
    sessionCleanup();
  });

  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "hidden") {
      setTimeout(function () {
        if (document.visibilityState === "hidden") {
          sessionCleanup();
        }
      }, 300000);
    }
  });

  startSessionHeartbeat();
}

function startSessionHeartbeat() {
  heartbeatInterval = setInterval(function () {
    try {
      localStorage.setItem("sessionHeartbeat", Date.now().toString());
    } catch (e) {
      console.error("Heartbeat update failed:", e);
    }
  }, 300000);
}

function sessionCleanup() {
  try {
    if (heartbeatInterval) {
      clearInterval(heartbeatInterval);
    }
  } catch (error) {
    console.error("Session cleanup failed:", error);
  }
}

export function initializePageProtection() {
  window.addEventListener("beforeunload", function (event) {
    if (window.isValidationInProgress || window.isIntentionalNavigation) {
      return;
    }

    const hasParsedData = window.parsedData !== null;
    const hasValidationData = window.validationData !== null;

    if (hasParsedData || hasValidationData) {
      const message =
        "All data will be erased if you refresh the page. Are you sure you want to continue?";
      event.preventDefault();
      event.returnValue = message;
      return message;
    }
  });
}

export function initializeDataHandling() {
  initializeGlobalDataAccess();
}

export function initializeGlobalDataAccess() {
  window.validationData = window.validationData || null;
  window.parsedData = window.parsedData || null;
}

export function cleanUpURLParameter() {
  const urlParams = new URLSearchParams(window.location.search);
  const hasValidationComplete = urlParams.get("validation_complete");
  const hasUploadComplete = urlParams.get("upload_complete");
  if (hasValidationComplete || hasUploadComplete) {
    window.isValidationInProgress = false;
    window.isIntentionalNavigation = false;

    const newUrl = window.location.pathname;
    window.history.replaceState({}, document.title, newUrl);
  }
}
