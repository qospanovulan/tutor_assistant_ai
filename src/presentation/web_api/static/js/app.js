function scrollChatToBottom() {
  const el = document.querySelector("[data-chat-scroll]");
  if (!el) return;
  el.scrollTop = el.scrollHeight;
}

document.addEventListener("DOMContentLoaded", () => {
  scrollChatToBottom();
});

// after HTMX swaps chat content, auto-scroll
document.body.addEventListener("htmx:afterSwap", (evt) => {
  // only when chat pane updated
  if (evt.target && (evt.target.id === "chat-pane" || evt.target.querySelector?.("#chat-pane"))) {
    scrollChatToBottom();
  }
});

// prevent double submit on choice buttons
document.body.addEventListener("htmx:beforeRequest", (evt) => {
  const btn = evt.target?.querySelector?.("button[type='submit']");
  if (btn) {
    btn.disabled = true;
    btn.classList.add("opacity-60");
  }
});
