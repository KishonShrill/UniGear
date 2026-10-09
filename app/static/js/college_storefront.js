/**
 * UniGear - College Storefront Interactive Controller
 * Handles organization fetching, search filtering, category tabs,
 * asynchronous merchandise rendering, and wishlist toggling.
 */

document.addEventListener("DOMContentLoaded", function () {
  const mainEl = document.querySelector("main[data-college]");
  if (!mainEl) return;

  const collegeCode = mainEl.getAttribute("data-college").toLowerCase();
  const productsContainer = document.getElementById("org-products");
  const typeTabs = document.querySelectorAll("#type-tabs .type-tab");
  const orgTabsContainer = document.getElementById("org-list");
  const orgSearchInput = document.getElementById("orgSearchInput");
  const orgCountPill = document.getElementById("orgCountPill");
  const activeOrgNameEl = document.getElementById("activeOrgName");
  const activeOrgCountEl = document.getElementById("activeOrgCount");

  let allOrganizations = [];
  let selectedOrgId = null;
  let selectedOrgName = "";
  let selectedType = "all";

  // CSRF helper
  function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute("content") : "";
  }

  // 1. Render Skeleton Loading State
  function renderSkeletonLoading(count = 6) {
    if (!productsContainer) return;
    let skeletonHtml = "";
    for (let i = 0; i < count; i++) {
      skeletonHtml += `
        <div class="skeleton-card" aria-hidden="true">
          <div class="skeleton-media"></div>
          <div class="skeleton-content">
            <div class="skeleton-line short"></div>
            <div class="skeleton-line title"></div>
            <div class="skeleton-line"></div>
            <div class="skeleton-line short"></div>
          </div>
        </div>
      `;
    }
    productsContainer.innerHTML = skeletonHtml;
  }

  // 2. Fetch Organizations for this College
  fetch(`/api/${collegeCode}/organizations`)
    .then((response) => {
      if (!response.ok) throw new Error("Network response was not ok");
      return response.json();
    })
    .then((organizations) => {
      allOrganizations = organizations || [];
      if (orgCountPill) {
        orgCountPill.textContent = `${allOrganizations.length} Orgs`;
      }

      renderOrganizationList(allOrganizations);

      // Select first organization automatically
      if (allOrganizations.length > 0) {
        selectOrganization(allOrganizations[0].id, allOrganizations[0].name);
      } else {
        if (productsContainer) {
          productsContainer.innerHTML = `
            <div class="empty-products-stage">
              <div class="empty-icon-circle">
                <i class="fas fa-university"></i>
              </div>
              <h3>No Organizations Found</h3>
              <p>There are currently no accredited student organizations listed under this college.</p>
            </div>
          `;
        }
      }
    })
    .catch((error) => {
      console.error("Error fetching organizations:", error);
      if (productsContainer) {
        productsContainer.innerHTML = `
          <div class="empty-products-stage">
            <div class="empty-icon-circle" style="color: #ef4444;">
              <i class="fas fa-exclamation-triangle"></i>
            </div>
            <h3>Unable to Load Organizations</h3>
            <p>We encountered an issue connecting to the server. Please refresh the page to try again.</p>
          </div>
        `;
      }
    });

  // 3. Render Organization List in Sidebar
  function renderOrganizationList(orgs) {
    if (!orgTabsContainer) return;
    orgTabsContainer.innerHTML = "";

    if (orgs.length === 0) {
      orgTabsContainer.innerHTML = `
        <li style="padding: 1rem; text-align: center; color: #94a3b8; font-size: 0.8125rem;">
          No matching organizations
        </li>
      `;
      return;
    }

    orgs.forEach((org) => {
      const li = document.createElement("li");
      li.className = "org-tab";
      li.setAttribute("data-org-id", org.id);
      li.setAttribute("role", "button");
      li.setAttribute("tabindex", "0");

      const isCouncil =
        org.name.toLowerCase().includes("council") ||
        org.name.toLowerCase().includes("executive") ||
        org.name.toLowerCase().includes("student council");
      if (isCouncil) {
        li.classList.add("council");
      }

      const iconClass = isCouncil ? "fas fa-award" : "fas fa-users";

      li.innerHTML = `
        <i class="${iconClass}"></i>
        <span class="org-name-text">${org.name}</span>
      `;

      if (selectedOrgId && org.id === selectedOrgId) {
        li.classList.add("active");
      }

      li.addEventListener("click", function () {
        selectOrganization(org.id, org.name);
      });

      li.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          selectOrganization(org.id, org.name);
        }
      });

      orgTabsContainer.appendChild(li);
    });
  }

  // 4. Select Organization Action
  function selectOrganization(orgId, orgName) {
    selectedOrgId = orgId;
    selectedOrgName = orgName;

    // Update active class in list
    document.querySelectorAll(".org-tab").forEach((tab) => {
      if (parseInt(tab.getAttribute("data-org-id")) === orgId) {
        tab.classList.add("active");
      } else {
        tab.classList.remove("active");
      }
    });

    // Update banner text
    if (activeOrgNameEl) {
      activeOrgNameEl.textContent = orgName;
    }

    loadProductsForOrg(orgId);
  }

  // 5. Search / Filter Organizations in Sidebar
  if (orgSearchInput) {
    orgSearchInput.addEventListener("input", function (e) {
      const query = e.target.value.toLowerCase().trim();
      const filtered = allOrganizations.filter((org) =>
        org.name.toLowerCase().includes(query)
      );
      renderOrganizationList(filtered);
    });
  }

  // 6. Category (Type) Filter Tabs
  typeTabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      const typeName = tab.getAttribute("data-type") || "all";
      selectedType = typeName.toLowerCase();

      typeTabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");

      if (selectedOrgId) {
        loadProductsForOrg(selectedOrgId);
      }
    });
  });

  // 7. Load & Render Products for an Organization
  function loadProductsForOrg(orgId) {
    renderSkeletonLoading(4);

    fetch(`/api/organizations/products?org_id=${orgId}&type=${selectedType}`)
      .then((response) => {
        if (!response.ok) throw new Error("Network error fetching products");
        return response.json();
      })
      .then((products) => {
        if (!productsContainer) return;

        if (activeOrgCountEl) {
          activeOrgCountEl.textContent = `${products.length} Items`;
        }

        if (!products || products.length === 0) {
          const typeLabel =
            selectedType !== "all" ? `in "${selectedType}"` : "";
          productsContainer.innerHTML = `
            <div class="empty-products-stage">
              <div class="empty-icon-circle">
                <i class="fas fa-box-open"></i>
              </div>
              <h3>No Merchandise Available</h3>
              <p>There are currently no active products ${typeLabel} for ${selectedOrgName}.</p>
              ${
                selectedType !== "all"
                  ? '<button type="button" class="btn-reset-filters" id="resetTypeBtn"><i class="fas fa-th-large"></i> View All Categories</button>'
                  : ""
              }
            </div>
          `;

          const resetBtn = document.getElementById("resetTypeBtn");
          if (resetBtn) {
            resetBtn.addEventListener("click", function () {
              selectedType = "all";
              typeTabs.forEach((t) => {
                if (t.getAttribute("data-type") === "all") {
                  t.classList.add("active");
                } else {
                  t.classList.remove("active");
                }
              });
              loadProductsForOrg(selectedOrgId);
            });
          }
          return;
        }

        // Render Product Cards
        productsContainer.innerHTML = "";
        products.forEach((product) => {
          const card = document.createElement("div");
          card.className = "product-card";
          card.setAttribute("data-product-id", product.id);

          const imgSrc =
            product.picture || "/static/images/placeholder.jpg";
          const formattedPrice =
            product.price !== undefined
              ? `₱${Number(product.price).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
              : "₱0.00";
          const orderTypeBadge =
            product.order_type === 1
              ? '<span class="badge-order-type time"><i class="fas fa-clock"></i> Time-Based</span>'
              : '<span class="badge-order-type goal"><i class="fas fa-bullseye"></i> Goal-Based</span>';

          const categoryTag = product.type
            ? `<div class="product-category-tag">${product.type}</div>`
            : "";
          const subtitle = product.hook || product.description || "";

          card.innerHTML = `
            <div class="product-card-media">
              <div class="card-floating-badges">
                ${orderTypeBadge}
              </div>
              <button type="button" class="favorite-btn ${product.is_favorite ? "favorited" : ""}" data-product-id="${product.id}" title="Add to Wishlist" aria-label="Toggle wishlist">
                <i class="fas fa-heart"></i>
              </button>
              <a href="/product/${product.id}">
                <img src="${imgSrc}" alt="${product.name}" loading="lazy">
              </a>
            </div>
            <div class="product-card-body">
              ${categoryTag}
              <a href="/product/${product.id}" style="text-decoration: none; color: inherit;">
                <h3 class="product-card-title">${product.name}</h3>
              </a>
              <p class="product-card-desc">${subtitle}</p>
              <div class="product-card-footer">
                <div class="product-price-box">
                  <span class="price-label">Price</span>
                  <span class="price-value">${formattedPrice}</span>
                </div>
                <a href="/product/${product.id}" class="btn-card-action">
                  <span>View Details</span>
                  <i class="fas fa-arrow-right"></i>
                </a>
              </div>
            </div>
          `;

          productsContainer.appendChild(card);
        });
      })
      .catch((error) => {
        console.error("Error fetching products:", error);
        if (productsContainer) {
          productsContainer.innerHTML = `
            <div class="empty-products-stage">
              <div class="empty-icon-circle" style="color: #ef4444;">
                <i class="fas fa-exclamation-circle"></i>
              </div>
              <h3>Failed to Load Products</h3>
              <p>Could not load merchandise for this organization. Please try again.</p>
            </div>
          `;
        }
      });
  }

  // 8. Wishlist Heart Toggle Listener with CSRF Verification
  if (productsContainer) {
    productsContainer.addEventListener("click", function (event) {
      const favoriteBtn = event.target.closest(".favorite-btn");
      if (!favoriteBtn) return;

      event.preventDefault();
      event.stopPropagation();

      const productId = favoriteBtn.getAttribute("data-product-id");
      if (!productId) return;

      const csrfToken = getCsrfToken();

      fetch("/favorite/submit", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ product_id: productId }),
      })
        .then((response) => {
          if (response.status === 401) {
            alert("Please sign in to save items to your wishlist.");
            return null;
          }
          return response.json();
        })
        .then((data) => {
          if (!data) return;
          if (data.success) {
            if (data.favorite_status) {
              favoriteBtn.classList.add("favorited");
            } else {
              favoriteBtn.classList.remove("favorited");
            }
          } else {
            alert(data.message || "An error occurred updating wishlist.");
          }
        })
        .catch((error) => {
          console.error("Error toggling favorite:", error);
        });
    });
  }
});
