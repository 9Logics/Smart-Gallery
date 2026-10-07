
>     <script>
      window.onerror = function(message, source, lineno, colno, error) {
          const errorDiv = document.createElement('div');
          errorDiv.style.position = 'fixed';
          errorDiv.style.top = '0';
          errorDiv.style.left = '0';
          errorDiv.style.width = '100vw';
          errorDiv.style.height = '100vh';
          errorDiv.style.backgroundColor = 'rgba(255, 0, 0, 0.9)';
          errorDiv.style.color = 'white';
          errorDiv.style.zIndex = '999999';
          errorDiv.style.padding = '40px';
          errorDiv.style.fontFamily = 'monospace';
          errorDiv.style.fontSize = '18px';
          errorDiv.style.overflow = 'auto';
          errorDiv.innerHTML = '<h1 class="siena-layer" data-depth="40">JAVASCRIPT ERROR</h1>' +
              '<p><b>Message:</b> ' + message + '</p>' +
              '<p><b>Source:</b> ' + source + ' : ' + lineno + ':' + colno + '</p>' +
              '<pre>' + (error && error.stack ? error.stack : 'No stack trace') + '</pre>';
          if (document.body) { document.body.appendChild(errorDiv); } else { document.documentElement.appendChild(errorDiv); }
          return false;
      };
      window.onunhandledrejection = function(event) {
          const errorDiv = document.createElement('div');
          errorDiv.style.position = 'fixed';
          errorDiv.style.top = '0';
          errorDiv.style.left = '0';
          errorDiv.style.width = '100vw';
          errorDiv.style.height = '100vh';
          errorDiv.style.backgroundColor = 'rgba(255, 100, 0, 0.9)';
          errorDiv.style.color = 'white';
          errorDiv.style.zIndex = '999999';
          errorDiv.style.padding = '40px';
          errorDiv.style.fontFamily = 'monospace';
          errorDiv.style.fontSize = '18px';
          errorDiv.style.overflow = 'auto';
          errorDiv.innerHTML = '<h1 class="siena-layer" data-depth="40">UNHANDLED PROMISE REJECTION</h1>' +
              '<p><b>Reason:</b> ' + event.reason + '</p>' +
              '<pre>' + (event.reason && event.reason.stack ? event.reason.stack : '') + '</pre>';
          if (document.body) { document.body.appendChild(errorDiv); } else { document.documentElement.appendChild(errorDiv); }
      };
      </script>
  
      <meta charset="UTF-8">
>     <script>
      if (window.location.href.indexOf('nocache=') === -1) {
          window.addEventListener('DOMContentLoaded', function() {
              var legacyInput = document.getElementById('edit-date-year');
              if (legacyInput && legacyInput.type === 'text') {
                  var sep = window.location.href.indexOf('?') === -1 ? '?' : '&';
                  window.location.replace(window.location.href + sep + 'nocache=' + new Date().getTime());
              }
          });
      }
      </script>
      
      <!-- PWA Manifest & Meta -->
      <link rel="manifest" href="/static/manifest.json">
      <meta name="theme-color" content="#1a1b1e">
      <link rel="icon" type="image/png" href="/static/icons/icon-192.png">
      
      <!-- Google Fonts -->
      <link rel="preconnect" href="https://fonts.googleapis.com">
      <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
      
      <!-- Leaflet JS Map CDN -->
      <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
      <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
      
      <!-- Leaflet MarkerCluster -->
      <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
      <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
      <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
      <script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
      
      <!-- Lucide Icons CDN -->
      <script src="https://unpkg.com/lucide@latest"></script>
      
      
      <!-- Stylesheet -->
      <link rel="stylesheet" href="/static/style.css?v=348">
      <link rel="stylesheet" href="/static/select_modernizer.css?v=348">
  
      <!-- Phase 1: High-End UI Libraries -->
      <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
      <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
  </head>
  <body class="dark-theme">
      <div class="app-container">
          
          <!-- Sidebar Navigation -->
          {% include 'partials/sidebar.html' %}
          
          <!-- Main Content Area -->
          <main class="main-content">
              
              <!-- Top Action Header -->
              <header class="top-header">
                  <div class="search-container">
                      <i data-lucide="search" class="search-icon"></i>
                      <input type="text" id="search-input" placeholder=" " autocomplete="off">
                      <div id="search-placeholder-loop" class="search-placeholder-loop">
                          <span class="static-text">Search for</span>
                          <span class="loop-container">
                              <span class="loop-item">"videos from last summer"</span>
                              <span class="loop-item">"New York City"</span>
                              <span class="loop-item">"mom and dad"</span>
                              <span class="loop-item">"sunset at the beach"</span>
                              <span class="loop-item">"IMG_4021"</span>
                              <span class="loop-item">"golden retriever"</span>
                              <span class="loop-item">"August 2023"</span>
                              <span class="loop-item">"wedding"</span>
                          </span>
                      </div>
                      <span class="search-kbd" id="search-kbd">Ctrl K</span>
                      <button id="clear-search-btn" class="hidden"><i data-lucide="x"></i></button>
                      <!-- Search Autocomplete Suggestions -->
                      <div id="search-suggestions" class="search-suggestions hidden"></div>
                  </div>
                  
                  <div class="header-actions">
                      <!-- Multi-select Action Bar -->
                      <div id="multiselect-bar" class="multiselect-bar hidden">
                          <span id="select-count">0 selected</span>
                          <div class="multiselect-actions">
                              <button id="multi-album-btn" class="btn btn-secondary">
                                  <i data-lucide="folder-plus"></i> Add to Album
                              </button>
                              <button id="multi-copy-btn" class="btn btn-secondary" title="Copy photo image to clipboard (Ctrl+V to paste in Discord/etc)">
                                  <i data-lucide="copy" style="width:16px; height:16px;"></i> Copy Photo
                              </button>
                              <button id="multi-archive-btn" class="btn btn-secondary" title="Archive selected photos">
                                  <i data-lucide="archive" style="width:16px; height:16px;"></i> Archive
                              </button>
                              <button id="multi-trash-btn" class="btn btn-danger" title="Move selected to Trash">
                                  <i data-lucide="trash-2" style="width:16px; height:16px;"></i> Move to Trash
                              </button>
                              <button id="multi-deselect-btn" class="btn btn-icon" onclick="clearSelection()" title="Clear selection">
                                  <i data-lucide="x"></i>
                              </button>
                          </div>
                      </div>
                      
>     <script>
          if ('serviceWorker' in navigator) {
              window.addEventListener('load', () => {
                  navigator.serviceWorker.register('/static/sw.js')
                      .then(registration => console.log('SW registered:', registration))
                      .catch(error => console.log('SW registration failed:', error));
              });
          }
      </script>
  
> <script>
      document.addEventListener('DOMContentLoaded', () => {
          const sidebar = document.querySelector('.sidebar');
          const toggleBtn = document.getElementById('sidebar-toggle');
          const settingToggle = document.getElementById('setting-compact-sidebar');
          
          // Restore saved state: Default is compact (true). Expanded is false.
          // The setting is "Compact Sidebar". If unchecked, it means expanded.
          const isCompact = localStorage.getItem('sidebar_compact') !== 'false';
          
          if (!isCompact) {
              sidebar.classList.add('expanded');
          }
          if (settingToggle) {
              settingToggle.checked = isCompact;
          }
  
          const toggleSidebar = () => {
              const currentlyExpanded = sidebar.classList.contains('expanded');
              if (currentlyExpanded) {
                  sidebar.classList.remove('expanded');
                  localStorage.setItem('sidebar_compact', 'true');
                  if(settingToggle) settingToggle.checked = true;
              } else {
                  sidebar.classList.add('expanded');
                  localStorage.setItem('sidebar_compact', 'false');
                  if(settingToggle) settingToggle.checked = false;
              }
          };
  
          if(toggleBtn) toggleBtn.addEventListener('click', toggleSidebar);
          if(settingToggle) {
              settingToggle.addEventListener('change', (e) => {
                  if (e.target.checked) {
                      sidebar.classList.remove('expanded');
                      localStorage.setItem('sidebar_compact', 'true');
                  } else {
                      sidebar.classList.add('expanded');
                      localStorage.setItem('sidebar_compact', 'false');
                  }
              });
          }
      });
  </script>
      <script src="/static/js/select_modernizer.js?v=348"></script>
  
  
  
>     <script>
      document.addEventListener('DOMContentLoaded', () => {
          const sortBtn = document.getElementById('win11-sort-btn');
          const sortMenu = document.getElementById('win11-sort-menu');
          const sortSelect = document.getElementById('sort-select');
          
          if(!sortBtn || !sortMenu || !sortSelect) return;
          
          let currentBy = 'date';
          let currentOrder = 'desc';
  
          sortBtn.addEventListener('click', (e) => {
              e.stopPropagation();
              sortMenu.classList.toggle('hidden');
              const fMenu = document.getElementById('win11-filter-menu');
              if (fMenu && !fMenu.classList.contains('hidden')) {
                  fMenu.classList.add('hidden');
              }
          });
  
          document.addEventListener('click', (e) => {
              if (!sortBtn.contains(e.target) && !sortMenu.contains(e.target)) {
                  sortMenu.classList.add('hidden');
              }
          });
  
          const updateUI = () => {
              document.querySelectorAll('#win11-group-by .win11-menu-item').forEach(el => {
                  if (el.dataset.sortBy === currentBy) {
                      el.classList.add('active');
                      el.querySelector('.win11-dot').classList.remove('hidden');
                  } else {
                      el.classList.remove('active');
                      el.querySelector('.win11-dot').classList.add('hidden');
                  }
              });
              document.querySelectorAll('#win11-group-order .win11-menu-item').forEach(el => {
                  if (el.dataset.sortOrder === currentOrder) {
                      el.classList.add('active');
                      el.querySelector('.win11-dot').classList.remove('hidden');
                  } else {
                      el.classList.remove('active');
                      el.querySelector('.win11-dot').classList.add('hidden');
                  }
              });
              
              let selectVal = currentBy + "_" + currentOrder;
              if (currentBy === 'type') selectVal = 'type_asc';
              
              sortSelect.value = selectVal;
              sortSelect.dispatchEvent(new Event('change'));
              lucide.createIcons(); // Re-render icons if needed
          };
  
          document.querySelectorAll('#win11-group-by .win11-menu-item').forEach(item => {
              item.addEventListener('click', () => {
                  currentBy = item.dataset.sortBy;
                  updateUI();
                  sortMenu.classList.add('hidden');
              });
          });
  
          document.querySelectorAll('#win11-group-order .win11-menu-item').forEach(item => {
              item.addEventListener('click', () => {
                  currentOrder = item.dataset.sortOrder;
                  updateUI();
                  sortMenu.classList.add('hidden');
              });
          });
  
          const filterBtn = document.getElementById('win11-filter-btn');
          const filterMenu = document.getElementById('win11-filter-menu');
          
          if (filterBtn && filterMenu) {
              let currentFilter = 'all'; // all, photos, videos
  
              filterBtn.addEventListener('click', (e) => {
                  e.stopPropagation();
                  filterMenu.classList.toggle('hidden');
                  if (sortMenu && !sortMenu.classList.contains('hidden')) {
                      sortMenu.classList.add('hidden');
                  }
              });
  
              document.addEventListener('click', (e) => {
                  if (!filterBtn.contains(e.target) && !filterMenu.contains(e.target)) {
                      filterMenu.classList.add('hidden');
                  }
              });
  
              const updateFilterUI = () => {
                  document.querySelectorAll('#win11-group-filter .win11-menu-item').forEach(el => {
                      if (el.dataset.filterType === currentFilter) {
                          el.classList.add('active');
                          el.querySelector('.win11-dot').classList.remove('hidden');
                      } else {
                          el.classList.remove('active');
                          el.querySelector('.win11-dot').classList.add('hidden');
                      }
                  });
                  
>     <script>
          function toggleRecap() {
              const body = document.body;
              body.classList.toggle('recap-active');
              
              if (body.classList.contains('recap-active')) {
                  // Set up Sleek Dashboard Preloader
                  const preloader = document.getElementById('pixel-preloader');
                  const wordEl = document.getElementById('pixel-counter');
                  const progressEl = document.getElementById('pixel-grid');
                  
                  preloader.style.display = 'flex';
                  preloader.style.opacity = '1';
                  progressEl.style.width = '0%';
                  
                  
  
                  // Set up Skiper27 Rolling Text
                  const title = document.getElementById('recap-title');
                  title.innerHTML = '';
                  title.classList.remove('revealed');
                  
                  const text = "Your Rewinds"; // We rely on font-display without uppercase now
                  text.split('').forEach((char, i) => {
                      const wrapper = document.createElement('span');
                      wrapper.className = 'roll-char-wrap';
                      
                      const inner = document.createElement('span');
                      inner.className = 'roll-char';
                      inner.innerText = char === ' ' ? '\u00A0' : char;
                      // Custom speed: 0.05 delay between letters
                      inner.style.transitionDelay = (i * 0.05) + 's';
                      
                      wrapper.appendChild(inner);
                      title.appendChild(wrapper);
                  });
  
                  // Simulate Loading
                  const loadingWords = ["GATHERING", "ANALYZING", "CURATING", "MAPPING", "READY."];
                  let wIndex = 0;
                  let count = 0;
                  wordEl.innerText = loadingWords[0];
                  
                  // GSAP word change animation
                  if (window.gsap) gsap.fromTo(wordEl, { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4, ease: "power3.out" });
  
                  const wordInterval = setInterval(() => {
                      wIndex++;
                      if (wIndex >= loadingWords.length - 1) {
                          clearInterval(wordInterval);
                      } else {
                          if (window.gsap) {
                              gsap.fromTo(wordEl, { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4, ease: "power3.out" });
                          }
                          wordEl.innerText = loadingWords[wIndex];
                      }
                  }, 400);
  
                  const interval = setInterval(() => {
                      count += Math.random() * 12 + 5;
                      if (count >= 100) {
                          count = 100;
                          clearInterval(interval);
                          clearInterval(wordInterval);
                          
                          wordEl.innerText = loadingWords[loadingWords.length - 1]; // "READY."
                          progressEl.style.width = '100%';
                          
                          title.classList.add('revealed');
                          
                          setTimeout(() => {
                              if (window.gsap) {
                                  gsap.to(preloader, { opacity: 0, duration: 0.8, onComplete: () => {
                                      preloader.style.display = 'none';
                                  }});
                              } else {
                                  preloader.style.opacity = '0';
                                  setTimeout(() => preloader.style.display = 'none', 800);
                              }
                              
                              setTimeout(() => {
                                  document.getElementById('recap-container').classList.add('options-active');
                                  document.getElementById('rewind-dashboard').classList.add('active');
                              }, 500);
                          }, 400);
                      } else {
                          progressEl.style.width = count + '%';
                      }
                  }, 100);
              }
          }
      </script>
  
      <!-- RECAP PLAYER OVERLAY -->
      <div id="recap-player-overlay" class="hidden">
          
          <!-- SVG Filter for Gooey Theme -->
          <svg style="position: absolute; width: 0; height: 0; pointer-events: none;">
              <defs>
                  <filter id="recap-goo">
                      <feGaussianBlur in="SourceGraphic" stdDeviation="40" result="blur"></feGaussianBlur>

