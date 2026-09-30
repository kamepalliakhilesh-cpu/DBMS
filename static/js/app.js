/**
 * DISASTER RELIEF RESOURCE MANAGEMENT SYSTEM
 * Frontend JavaScript Controller & Interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    // ------------------------------------------------------------------------
    // 1. MODAL CONTROLLER
    // ------------------------------------------------------------------------
    const openModalButtons = document.querySelectorAll('[data-modal-open]');
    const closeModalButtons = document.querySelectorAll('[data-modal-close]');
    const modalBackdrops = document.querySelectorAll('.modal-backdrop');

    openModalButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = btn.getAttribute('data-modal-open');
            const targetModal = document.getElementById(targetId);
            if (targetModal) {
                targetModal.classList.add('show');
                const firstInput = targetModal.querySelector('input:not([type=hidden]), select');
                if (firstInput) firstInput.focus();
            }
        });
    });

    closeModalButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal-backdrop');
            if (modal) modal.classList.remove('show');
        });
    });

    modalBackdrops.forEach(backdrop => {
        backdrop.addEventListener('click', (e) => {
            if (e.target === backdrop) {
                backdrop.classList.remove('show');
            }
        });
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            modalBackdrops.forEach(m => m.classList.remove('show'));
        }
    });

    // ------------------------------------------------------------------------
    // 2. EDIT MODAL PRE-FILL HANDLER
    // ------------------------------------------------------------------------
    const editButtons = document.querySelectorAll('[data-edit-data]');
    editButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const rawData = btn.getAttribute('data-edit-data');
            const modalId = btn.getAttribute('data-modal-open');
            const modal = document.getElementById(modalId);
            if (!rawData || !modal) return;

            try {
                const data = JSON.parse(rawData);
                Object.keys(data).forEach(key => {
                    const input = modal.querySelector(`[name="${key}"]`);
                    if (input) {
                        input.value = data[key] !== null ? data[key] : '';
                    }
                });
            } catch (err) {
                console.error("Error parsing edit data:", err);
            }
        });
    });

    // ------------------------------------------------------------------------
    // 3. LIVE TABLE SEARCH & FILTERING (Instant Client-side)
    // ------------------------------------------------------------------------
    const clientSearchInputs = document.querySelectorAll('[data-table-search]');
    clientSearchInputs.forEach(input => {
        const tableId = input.getAttribute('data-table-search');
        const table = document.getElementById(tableId);
        if (!table) return;

        input.addEventListener('input', () => {
            const query = input.value.toLowerCase().trim();
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    });

    // ------------------------------------------------------------------------
    // 4. SQL QUERY RUNNER & COPY UTILS (Reports Page)
    // ------------------------------------------------------------------------
    const sqlTextarea = document.getElementById('sql_query');
    const sampleQueryCards = document.querySelectorAll('[data-load-sql]');

    sampleQueryCards.forEach(card => {
        card.addEventListener('click', () => {
            const sql = card.getAttribute('data-load-sql');
            if (sqlTextarea && sql) {
                sqlTextarea.value = sql;
                sqlTextarea.scrollIntoView({ behavior: 'smooth', block: 'center' });
                sqlTextarea.focus();
                showToast("Query loaded into SQL Editor. Click 'Execute SQL' to run.", "info");
            }
        });
    });

    // AJAX Run SQL (if quick run is clicked)
    const ajaxRunBtn = document.getElementById('btn-ajax-run');
    if (ajaxRunBtn && sqlTextarea) {
        ajaxRunBtn.addEventListener('click', async () => {
            const sql = sqlTextarea.value.trim();
            if (!sql) {
                showToast("Please enter an SQL query first.", "warning");
                return;
            }

            const resultsContainer = document.getElementById('sql-results-container');
            if (resultsContainer) {
                resultsContainer.innerHTML = '<div style="padding: 1.5rem; text-align: center; color: var(--accent-cyan);"><i class="fas fa-spinner fa-spin"></i> Executing query...</div>';
            }

            try {
                const resp = await fetch('/api/run-sql', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sql })
                });
                const data = await resp.json();

                if (data.success && resultsContainer) {
                    let html = '';
                    data.results.forEach((block, idx) => {
                        html += `<div class="card-panel" style="margin-bottom: 1rem;">
                            <div class="card-title" style="font-size: 1rem;">
                                <span><i class="fas fa-terminal"></i> Query: <code>${escapeHtml(block.query)}</code></span>
                                <span class="badge ${block.type === 'SELECT' ? 'badge-moderate' : 'badge-low'}">${block.type}</span>
                            </div>`;

                        if (block.type === 'SELECT') {
                            if (block.rows.length === 0) {
                                html += `<p style="color: var(--text-muted); font-size: 0.9rem;">No matching rows returned.</p>`;
                            } else {
                                html += `<div class="table-responsive">
                                    <table class="table-custom">
                                        <thead>
                                            <tr>${block.columns.map(c => `<th>${escapeHtml(c)}</th>`).join('')}</tr>
                                        </thead>
                                        <tbody>
                                            ${block.rows.map(row => `
                                                <tr>${block.columns.map(c => `<td>${row[c] !== null ? escapeHtml(String(row[c])) : '<em style="color: var(--text-muted)">NULL</em>'}</td>`).join('')}</tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                                <div style="margin-top: 0.5rem; font-size: 0.8rem; color: var(--text-muted);">Returned ${block.rows.length} row(s)</div>`;
                            }
                        } else {
                            html += `<div class="alert alert-success" style="margin: 0;">${escapeHtml(block.message)}</div>`;
                        }
                        html += `</div>`;
                    });
                    resultsContainer.innerHTML = html;
                    showToast("Query executed successfully!", "success");
                } else if (resultsContainer) {
                    resultsContainer.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-triangle"></i> SQL Error: ${escapeHtml(data.error)}</div>`;
                    showToast("SQL Execution Error", "danger");
                }
            } catch (err) {
                if (resultsContainer) {
                    resultsContainer.innerHTML = `<div class="alert alert-danger">Network error executing query: ${escapeHtml(err.message)}</div>`;
                }
            }
        });
    }

    // ------------------------------------------------------------------------
    // 5. SIDEBAR MOBILE TOGGLE
    // ------------------------------------------------------------------------
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    // Auto dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(al => {
        setTimeout(() => {
            al.style.transition = 'opacity 0.5s ease';
            al.style.opacity = '0';
            setTimeout(() => al.remove(), 500);
        }, 5000);
    });
});

// Toast notification utility
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 999; display: flex; flex-direction: column; gap: 8px;';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.style.cssText = 'box-shadow: 0 4px 12px rgba(0,0,0,0.5); min-width: 260px; margin: 0;';
    toast.innerHTML = `<span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.transition = 'opacity 0.4s ease';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.toString().replace(/[&<>"']/g, m => map[m]);
}
