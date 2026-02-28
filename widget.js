(function () {
  const BACKEND_URL = "https://ai-chatbot-73ut.onrender.com/chat";
  const CLIENT_ID = document.currentScript.getAttribute("data-client") || "mikes-barbershop";
  const BOT_NAME = document.currentScript.getAttribute("data-name") || "Assistant";

  // Inject styles
  const style = document.createElement("style");
  style.innerHTML = `
    #cb-toggle {
      position: fixed; bottom: 24px; right: 24px;
      width: 60px; height: 60px; background: #2563eb;
      border-radius: 50%; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      box-shadow: 0 4px 12px rgba(0,0,0,0.2); z-index: 9999;
    }
    #cb-toggle svg { width: 28px; height: 28px; fill: white; }
    #cb-window {
      position: fixed; bottom: 100px; right: 24px;
      width: 340px; height: 480px; background: white;
      border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.15);
      display: none; flex-direction: column; z-index: 9999; overflow: hidden;
    }
    #cb-window.open { display: flex; }
    #cb-header {
      background: #2563eb; color: white; padding: 16px;
      font-weight: bold; font-size: 15px;
      display: flex; align-items: center; gap: 10px;
      font-family: Arial, sans-serif;
    }
    #cb-header span {
      width: 10px; height: 10px; background: #4ade80;
      border-radius: 50%; display: inline-block;
    }
    #cb-messages {
      flex: 1; padding: 16px; overflow-y: auto;
      display: flex; flex-direction: column; gap: 10px;
      font-family: Arial, sans-serif;
    }
    .cb-msg {
      max-width: 80%; padding: 10px 14px;
      border-radius: 12px; font-size: 14px; line-height: 1.4;
    }
    .cb-msg.bot {
      background: #f1f5f9; color: #1e293b;
      align-self: flex-start; border-bottom-left-radius: 4px;
    }
    .cb-msg.user {
      background: #2563eb; color: white;
      align-self: flex-end; border-bottom-right-radius: 4px;
    }
    .cb-msg.typing { background: #f1f5f9; color: #94a3b8; align-self: flex-start; font-style: italic; }
    #cb-input-area {
      padding: 12px; border-top: 1px solid #e2e8f0;
      display: flex; gap: 8px;
    }
    #cb-input {
      flex: 1; padding: 10px 14px; border: 1px solid #e2e8f0;
      border-radius: 24px; font-size: 14px; outline: none;
      font-family: Arial, sans-serif;
    }
    #cb-input:focus { border-color: #2563eb; }
    #cb-send {
      width: 40px; height: 40px; background: #2563eb;
      border: none; border-radius: 50%; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
    }
    #cb-send svg { width: 18px; height: 18px; fill: white; }
  `;
  document.head.appendChild(style);

  // Inject HTML
  document.body.innerHTML += `
    <div id="cb-toggle" onclick="cbToggle()">
      <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>
    </div>
    <div id="cb-window">
      <div id="cb-header"><span></span> ${BOT_NAME}</div>
      <div id="cb-messages">
        <div class="cb-msg bot">Hi! 👋 How can I help you today?</div>
      </div>
      <div id="cb-input-area">
        <input id="cb-input" type="text" placeholder="Type a message..." />
        <button id="cb-send">
          <svg viewBox="0 0 24 24"><path d="M2 21l21-9L2 3v7l15 2-15 2z"/></svg>
        </button>
      </div>
    </div>
  `;

  // Functions
  window.cbToggle = function () {
    document.getElementById("cb-window").classList.toggle("open");
  };

  document.addEventListener("click", function (e) {
    if (e.target.closest("#cb-send")) cbSend();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && document.getElementById("cb-input") === document.activeElement) cbSend();
  });

  async function cbSend() {
    const input = document.getElementById("cb-input");
    const messages = document.getElementById("cb-messages");
    const text = input.value.trim();
    if (!text) return;

    messages.innerHTML += `<div class="cb-msg user">${text}</div>`;
    input.value = "";
    messages.innerHTML += `<div class="cb-msg typing" id="cb-typing">Typing...</div>`;
    messages.scrollTop = messages.scrollHeight;

    try {
      const res = await fetch(BACKEND_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, client_id: CLIENT_ID })
      });
      const data = await res.json();
      document.getElementById("cb-typing").remove();
      messages.innerHTML += `<div class="cb-msg bot">${data.reply}</div>`;
    } catch {
      document.getElementById("cb-typing").remove();
      messages.innerHTML += `<div class="cb-msg bot">Sorry, something went wrong.</div>`;
    }

    messages.scrollTop = messages.scrollHeight;
  }
})();