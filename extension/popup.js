const output = document.getElementById("output");
const manualInput = document.getElementById("manualInput");
const toneSelect = document.getElementById("tone");

const apiKey = "YOUR_API_KEY"; // Replace with your actual API key
const penciloApiUrl = "https://zt1hqha9od.execute-api.eu-north-1.amazonaws.com/dev";
let improvedText = "";

document.getElementById("validateBtn").onclick = () => {
    const text = manualInput.value.trim();
    if (text.length >= 3) {
        output.value = "Validating...";
        getText("validate", text).then(result => {
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
        getText("rephrase", text, tone).then(result => {
            improvedText = result;
            output.value = result;
        });
    }
};

document.getElementById("copyBtn").addEventListener("click", () => {
    const outputText = output.value;
    if (outputText.trim()) {
        navigator.clipboard.writeText(outputText.trim())
            .then(() => {
                const btn = document.getElementById("copyBtn");
                btn.textContent = "Text copied!";
                setTimeout(() => (btn.textContent = "Copy to Clipboard"), 1500);
            })
            .catch(() => alert("Failed to copy to clipboard."));
    }
});

async function getText(action, text, tone = "default") {
    console.log(`Action: ${action}, Text: ${text}, Tone: ${tone}`);
    console.log(`API Key: ${apiKey}`);
    const response = await fetch(`${penciloApiUrl}/text`, {
        method: "POST",
        headers: {
            "x-api-key": apiKey,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            text,
            mode: action,
            tone
        })
    });

    const data = await response.json();

    if (data?.body?.error) {
        // TODO: Handle error response - show only specific error message like: "Invalid API key" but ignore other errors
        const errorMessage = data.body.error || "An error occurred.";
        console.log(`Error: ${errorMessage}`);
        return `${errorMessage}`;
    }

    let content = data?.body?.result;
    if (typeof content !== "string") {
        throw new Error("Invalid response from server.");
    }

    if ((content.startsWith('"') && content.endsWith('"')) ||
        (content.startsWith('“') && content.endsWith('”'))) {
        content = content.slice(1, -1);
    }

    return content;
}

document.addEventListener("DOMContentLoaded", () => {
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        chrome.tabs.sendMessage(tabs[0].id, {action: "getLastInputText"}, (response) => {
            if (response && response.text) {
                document.getElementById("manualInput").value = response.text;
            }
        });
    });
});

chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    chrome.tabs.sendMessage(
        tabs[0].id,
        {action: "getLastInputText"},
        (response) => {
            if (chrome.runtime.lastError) {
                console.warn("Content script not found:", chrome.runtime.lastError.message);
            } else {
                console.log("Response from content script:", response);
            }
        }
    );
});