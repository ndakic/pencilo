const output = document.getElementById("output");
const manualInput = document.getElementById("manualInput");
const toneSelect = document.getElementById("tone");

const apiKey = "YOUR_API_KEY"; // Replace with your OpenAI API key
const model = "gpt-4o-mini-2024-07-18";

let improvedText = "";

document.getElementById("validateBtn").onclick = () => {
  const text = manualInput.value.trim();
  if (text.length >= 3) {
    output.value = "Validating...";
    callOpenAI("validate", text).then(result => {
      improvedText = result;
      output.value = result;
    });
  }
};

document.getElementById("improveBtn").onclick = () => {
  const text = manualInput.value.trim();
  const tone = toneSelect.value;
  if (text.length >= 3) {
    output.value = "Improving...";
    callOpenAI("improve", text, tone).then(result => {
      improvedText = result;
      output.value = result;
    });
  }
};

// Call OpenAI from popup (manual input)
async function callOpenAI(action, text, tone = "default") {
  const systemPrompt = action === "validate"
    ? "You are a helpful assistant that validates grammar and fluency."
    : `You are a writing assistant. Improve the grammar, spelling, and clarity. Rewrite it with a ${tone} tone.`;

  const userPrompt = action === "validate"
    ? `Validate the following text. Make sure you always return the results text without any additional text. Do not add pre text like "Here is the corrected text", 
      "The text is correct or Corrected version. Return corrected version if needed, otherwise return original:\n\n"${text}. \n .`
    : `Please improve the following text with tone: ${tone}\n\n"${text}"`;

  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: model,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userPrompt }
      ]
    })
  });

  const data = await response.json();
  let content = data.choices[0].message.content.trim();
  if ((content.startsWith('"') && content.endsWith('"')) ||
      (content.startsWith('“') && content.endsWith('”'))) {
    content = content.slice(1, -1);
  }

  return content;
}

// On popup open, get currently focused input field content
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  chrome.tabs.sendMessage(tabs[0].id, { action: "getFocusedInputValue" }, (response) => {
    if (response && response.text) {
      const manualInput = document.getElementById("manualInput");
      if (manualInput) {
        manualInput.value = response.text;
      }
    }
  });
});


document.getElementById("copyBtn").addEventListener("click", () => {
  const outputText = document.getElementById("output").value;
  if (outputText.trim()) {
    navigator.clipboard.writeText(outputText.trim())
      .then(() => {
        const btn = document.getElementById("copyBtn");
        btn.textContent = "Text copied!";
        setTimeout(() => (btn.textContent = "Copy to Clipboard"), 1500);
      })
      .catch(() => {
        alert("Failed to copy to clipboard.");
      });
  }
});