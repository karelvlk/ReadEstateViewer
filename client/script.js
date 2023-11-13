const API_BASE_URL = "/api";

async function fetchTotalCount() {
  try {
    const response = await fetch(`${API_BASE_URL}/items-count`);
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    return await response.json();
  } catch (error) {
    console.error("There was a problem with the fetch operation:", error);
  }
}

function createPagination(totalItems, currentPage, pageSize = 20) {
  const totalPages = Math.ceil(totalItems / pageSize);
  let startPage, endPage;

  if (totalPages <= 7) {
    // Less than 7 total pages so show all
    startPage = 1;
    endPage = totalPages;
  } else {
    // More than 7 total pages so calculate start and end pages
    if (currentPage <= 4) {
      startPage = 1;
      endPage = 5;
    } else if (currentPage + 3 >= totalPages) {
      startPage = totalPages - 4;
      endPage = totalPages;
    } else {
      startPage = currentPage - 2;
      endPage = currentPage + 2;
    }
  }

  let paginationHtml = '<ul class="pagination">';

  // First Page
  if (startPage > 1) {
    paginationHtml += `<li class="page-item"><a href="#" onclick="displayData(1)">1</a></li>`;
    paginationHtml += '<li class="page-item">...</li>';
  }

  // Page Numbers
  for (let i = startPage; i <= endPage; i++) {
    paginationHtml += `<li class="page-item ${
      i === currentPage ? "active" : ""
    }"><a href="#" onclick="displayData(${i})">${i}</a></li>`;
  }

  // Last Page
  if (endPage < totalPages) {
    paginationHtml += '<li class="page-item">...</li>';
    paginationHtml += `<li class="page-item"><a href="#" onclick="displayData(${totalPages})">${totalPages}</a></li>`;
  }

  paginationHtml += "</ul>";
  return paginationHtml;
}

const fetchRealEstateData = async (page) => {
  try {
    const response = await fetch(`${API_BASE_URL}/items/${page}`);
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    return await response.json();
  } catch (error) {
    console.error("There was a problem with the fetch operation:", error);
  }
};

const createRealEstateElement = (item) => {
  const imageSrc = item.img_url;
  const element = document.createElement("div");
  element.className = "real-estate-item";
  element.innerHTML = `
        <label class="img-label">${item.title}</label>
        <img src="${imageSrc}" alt="${item.title}" />
    `;
  return element;
};

async function displayData(page) {
  const data = await fetchRealEstateData(page);
  const totalCount = (await fetchTotalCount()).total_items ?? 0;
  const contentDiv = document.getElementById("content");
  const paginationDiv = document.getElementById("footer");

  contentDiv.innerHTML = "";
  data.forEach((item) => {
    contentDiv.appendChild(createRealEstateElement(item));
  });

  paginationDiv.innerHTML = createPagination(totalCount, page);
}

displayData(1);
