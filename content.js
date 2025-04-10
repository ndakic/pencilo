let activeInput = null;
let icon = null;
let popup = null;
let outputTextarea = null;
let improvedText = "";
let validatedText = "";
let manualInputField = null;


function isEditable(el) {
  return (
    (el.tagName === "TEXTAREA") ||
    (el.tagName === "INPUT" && el.type === "text") ||
    (el.isContentEditable)
  );
}

function getInputText(el) {
  return el.isContentEditable ? el.innerText : el.value;
}


chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("Received message:", request);
  if (request.action === "validate") {
    const focused = document.activeElement;
    if (isEditable(focused)) {
      const text = getInputText(focused);
      if (text.length < 3) {
        sendResponse({ result: null });
        return;
      }
      validateText(text).then(result => {
        sendResponse({ result });
      });
      return true; // Keep message channel open
    }
  } else if (request.action === "improve") {
    const focused = document.activeElement;
    if (isEditable(focused)) {
      const text = getInputText(focused);
      if (text.length < 3) {
        sendResponse({ result: null });
        return;
      }
      improveText(text, request.tone || "default").then(result => {
        sendResponse({ result });
      });
      return true;
    }
  }
   else if (request.action === "replace") {
    const focused = document.activeElement;
    if (isEditable(focused)) {
      setInputText(focused, request.content);
    }
  }
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getFocusedInputValue") {
    const focused = document.activeElement;
    if (isEditable(focused)) {
      sendResponse({ text: getInputText(focused) });
    } else {
      sendResponse({ text: "" });
    }
  }
});
