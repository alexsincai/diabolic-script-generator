const aboutLink = document.querySelector("form + p > a");
const modal = document.querySelector("#about");
const backDrop = document.createElement("div");
const form = document.querySelector("form");

const closers = [
    modal.querySelector("header > a"),
    modal.querySelector("footer > button"),
];

const showModal = () => {
    document.body.classList.add("modal-open");
    modal.classList.add("show");
    modal.style.display = "block";
    backDrop.classList.add("modal-backdrop", "show");
    document.body.appendChild(backDrop);
};

const hideModal = () => {
    document.body.classList.remove("modal-open");
    modal.classList.remove("show");
    modal.style.display = "none";
    backDrop.classList.remove("modal-backdrop", "show");

    if (backDrop.parent === document.body) document.body.removeChild(backDrop);
};

aboutLink.addEventListener("click", (e) => {
    e.preventDefault();
    showModal();
});

closers.forEach((c) =>
    c.addEventListener("click", (e) => {
        e.preventDefault();
        hideModal();
    })
);

document.body.addEventListener("keyup", (e) => {
    if (e.key === "Escape") {
        hideModal();
    }
});

form.addEventListener("submit", async (e) => {
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
