// Centralized, importable UI/runtime flags.
// Using a module avoids brittle window globals and keeps state consistent across modules.
export const appFlags = {
  isProcessing: false,
  isValidationInProgress: false,
  isIntentionalNavigation: false,
};


