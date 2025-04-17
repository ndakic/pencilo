let lastFocusedText = "";

console.log("[AI Grammar Checker] content.js loaded");
// This script runs in the context of the web page

function isEditable(el) {
  return (
    (el.tagName === "TEXTAREA") ||
    (el.tagName === "INPUT" && el.type === "text") ||
    el.isContentEditable
  );
}

function getTextFromElement(el) {
  return el.isContentEditable ? el.innerText : el.value;
}

// Monitor focused inputs and keep track of text
document.addEventListener("focusin", (e) => {
  const el = e.target;
  if (isEditable(el)) {
    lastFocusedText = getTextFromElement(el);
  }
});

document.addEventListener("input", (e) => {
  const el = e.target;
  if (isEditable(el)) {
    lastFocusedText = getTextFromElement(el);
  }
});

// Listen for popup asking for text
chrome.runtime.onMessage.addListener((req, sender, sendResponse) => {
  if (req.action === "getLastInputText") {
    sendResponse({ text: lastFocusedText });
  }
});
