document.querySelector("form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = e.target.text;

    const request = await fetch(e.target.action, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text.value }),
    });

    if (request.ok) {
        const response = await request.json();

        const output = document.querySelector("#output");
        output.innerHTML = "";

        if (response.error) {
            const error = document.createElement("h2");
            error.innerText = response.error;

            output.appendChild(error);
        } else {
            const img = document.createElement("img");
            img.src = response.url;
            img.alt = text.value;

            output.appendChild(img);
        }

        text.focus();
    }
});
