document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-button");
  
    function appendMessage(message, sender) {
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
  
      fetch("/chat", {
        method: "POST",
        body: JSON.stringify({ message: text }),
        headers: { "Content-Type": "application/json" }
      })
      .then(response => response.json())
      .then(data => {
        setTimeout(() => {
          appendMessage(data.reply, "bot");
        }, 1000); // 1 second delay between user input and bot reply
      });
  
      userInput.value = "";
    }
  
    sendButton.addEventListener("click", sendUserMessage);
    userInput.addEventListener("keypress", function (e) {
      if (e.key === "Enter") sendUserMessage();
    });
  });
  