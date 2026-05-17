(function () {
  const collections = Array.isArray(window.NESSUNO_COLLECTIONS)
    ? window.NESSUNO_COLLECTIONS
    : [];

  const page = document.body.dataset.page;
  const pathPrefix = document.body.dataset.pathPrefix || "";

  const escapeHtml = (value) =>
    String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

  const withPrefix = (path) => `${pathPrefix}${path}`;

  const renderHome = () => {
    const stack = document.querySelector("#collection-stack");
    if (!stack) {
      return;
    }

    stack.innerHTML = collections
      .map((collection) => {
        const image = collection.images && collection.images[0];
        const imageMarkup = image
          ? `<img src="${escapeHtml(withPrefix(image.src))}" alt="${escapeHtml(image.alt)}" loading="lazy">`
          : `<span class="collection-image-placeholder" aria-hidden="true"></span>`;

        return `
          <a class="collection-row" href="collections/${escapeHtml(collection.slug)}/">
            <span class="collection-image">${imageMarkup}</span>
            <span class="collection-copy">
              <span class="collection-title">${escapeHtml(collection.title)}</span>
              <span class="collection-note">${escapeHtml(collection.note)}</span>
            </span>
          </a>
        `;
      })
      .join("");
  };

  const renderCollection = () => {
    const slug = document.body.dataset.collection;
    const collection = collections.find((item) => item.slug === slug);
    const title = document.querySelector("#collection-title");
    const grid = document.querySelector("#photo-grid");

    if (!collection || !title || !grid) {
      return;
    }

    document.title = `${collection.title} - Nessuno`;
    title.textContent = collection.title;
    grid.innerHTML = collection.images
      .map(
        (image) => `
          <figure class="photo-item">
            <img src="${escapeHtml(withPrefix(image.src))}" alt="${escapeHtml(image.alt)}" loading="lazy">
          </figure>
        `
      )
      .join("");
  };

  if (page === "home") {
    renderHome();
  }

  if (page === "collection") {
    renderCollection();
  }
})();
