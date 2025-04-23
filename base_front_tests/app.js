const baseUrl = "http://127.0.0.1:4567/api/v1/posts/";
let currentPage = 1;

async function loadPosts(page) {
  const params = new URLSearchParams({
    category: "fyi",
    page: page,
    is_exploded: "false",
    sort: "created_at"
  });

  const response = await fetch(`${baseUrl}?${params.toString()}`);
  if (!response.ok) {
    console.error("Ошибка загрузки:", response.status);
    return;
  }

  const posts = await response.json();
  const container = document.getElementById("posts-container");

  posts.forEach(post => {
    const postDiv = document.createElement("div");
    postDiv.className = "post";
    postDiv.innerHTML = `
      <h3>${post.title}</h3>
      <div class="meta">
        Автор: <strong>${post.author_username}</strong> | 
        Категория: <strong>${post.category_name}</strong> | 
        Дата: ${new Date(post.created_at).toLocaleString()}
      </div>
      <p>${post.content}</p>
    `;
    container.appendChild(postDiv);
  });
}

document.getElementById("load-more").addEventListener("click", () => {
  currentPage += 1;
  loadPosts(currentPage);
});

// Загрузка первой страницы при старте
loadPosts(currentPage);
