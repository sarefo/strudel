let filesData = [];
let currentSort = { 
    published: { column: 'modified', direction: 'desc' },
    building: { column: 'modified', direction: 'desc' },
    test: { column: 'modified', direction: 'desc' }
};

async function loadFiles() {
    try {
        // Load file list from JSON
        const response = await fetch('data/files.json');
        filesData = await response.json();
        
        renderTables();
        
    } catch (error) {
        console.error('Error loading files:', error);
        ['published', 'building', 'test'].forEach(stage => {
            const tableBody = document.getElementById(`${stage}TableBody`);
            tableBody.innerHTML = '<tr><td colspan="3" style="color: red; text-align: center;">Error loading files</td></tr>';
        });
    }
}

async function renderTables() {
    const stages = ['published', 'building', 'test'];
    
    for (const stage of stages) {
        const stageFiles = filesData.filter(file => file.stage === stage);
        await renderTable(stage, stageFiles);
    }
}

async function renderTable(stage, files) {
    const tableBody = document.getElementById(`${stage}TableBody`);
    tableBody.innerHTML = '';

    if (files.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="3" style="color: #999; text-align: center; font-style: italic;">No files in this stage</td></tr>';
        return;
    }

    for (const file of files) {
        try {
            // Load file content for encoding
            const response = await fetch(`files/${file.path}`);
            const content = await response.text();
            
            // Base64 encode the content (handle Unicode properly)
            const encoded = btoa(unescape(encodeURIComponent(content)));
            const strudelUrl = `https://strudel.cc/#${encoded}`;
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><a href="${strudelUrl}" target="_blank" class="file-link">${file.title}</a></td>
                <td>${file.author}</td>
                <td>${file.modified}</td>
            `;
            
            tableBody.appendChild(row);
        } catch (error) {
            console.error(`Error loading file ${file.filename}:`, error);
        }
    }
}

function sortTable(column, section) {
    if (currentSort[section].column === column) {
        currentSort[section].direction = currentSort[section].direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort[section].column = column;
        currentSort[section].direction = 'asc';
    }

    const sectionFiles = filesData.filter(file => file.stage === section);
    sectionFiles.sort((a, b) => {
        let aVal = a[column];
        let bVal = b[column];
        
        // Handle date sorting
        if (column === 'modified') {
            aVal = new Date(aVal);
            bVal = new Date(bVal);
        }
        
        if (aVal < bVal) return currentSort[section].direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return currentSort[section].direction === 'asc' ? 1 : -1;
        return 0;
    });

    // Update header classes for this section
    document.querySelectorAll(`th[data-section="${section}"]`).forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    
    const currentHeader = document.querySelector(`th[data-column="${column}"][data-section="${section}"]`);
    currentHeader.classList.add(currentSort[section].direction === 'asc' ? 'sort-asc' : 'sort-desc');

    renderTable(section, sectionFiles);
}

// Add click handlers to sortable headers
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('th.sortable').forEach(th => {
        th.addEventListener('click', () => {
            sortTable(th.dataset.column, th.dataset.section);
        });
    });
    
    loadFiles();
});