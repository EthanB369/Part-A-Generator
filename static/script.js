document.addEventListener("DOMContentLoaded", function () {
  const chatBox = document.getElementById("chat-box");
  const userInput = document.getElementById("user-input");
  const sendButton = document.getElementById("send-button");

  function appendMessage(message, sender) {
    console.log("SENDER:", sender);  // 👈 add this
    const messageElement = document.createElement("div");
    messageElement.classList.add(sender === "user" ? "user-message" : "bot-message");
    messageElement.innerHTML = message;
    chatBox.appendChild(messageElement);

    // Smooth scroll to bottom
    chatBox.scrollTo({
      top: chatBox.scrollHeight,
      behavior: "smooth"
    });
  }

  function sendUserMessage() {
    const text = userInput.value.trim();
    if (text === "") return;

    appendMessage(text, "user");
    userInput.value = "";

    fetch("/chat", {
      method: "POST",
      body: JSON.stringify({ message: text }),
      headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
      appendMessage(data.reply, "bot"); // First show feedback
    
      if (data.next) {
        setTimeout(() => {
          appendMessage(data.next, "bot"); // After delay, show next question
        }, 750); // 500ms or 1s up to you
      } 
    
    });
    
  }
  sendButton.addEventListener("click", sendUserMessage);
  userInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") sendUserMessage();
  });

// 👇 Send an initial welcome message automatically
window.addEventListener("load", () => {
  appendMessage("👋 Hi, I'm your Part A Mock Exam Generator! 🎓<br>Type <b>Start</b> to begin your mock exam! 🧠", "bot");
});

});