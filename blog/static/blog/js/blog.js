<script>
document.querySelectorAll(".react-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    fetch("{% url 'post_reaction' %}", {
      method: "POST",
      headers: {
        "X-CSRFToken": "{{ csrf_token }}",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        post_id: btn.dataset.id,
        reaction: btn.dataset.action
      })
    })
    .then(res => res.json())
    .then(data => {
      document.getElementById(`likes-${btn.dataset.id}`).innerText = data.likes;
      document.getElementById(`unlikes-${btn.dataset.id}`).innerText = data.unlikes;
    });
  });
});
</script>
