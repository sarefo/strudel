let docsFiles = [];

async function loadDocsFiles() {
    const container = document.getElementById('docsListContainer');
    
    try {
        const response = await fetch('../data/docs.json');
        docsFiles = await response.json();
        
        if (docsFiles.length === 0) {
            container.innerHTML = '<li>No markdown files found in the docs directory.</li>';
            return;
        }
        
        container.innerHTML = '';
        docsFiles.forEach(file => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = '#';
            a.textContent = file.title;
            a.onclick = (e) => {
                e.preventDefault();
                loadMarkdownFile(file.path, file.title);
            };
            
            // Add modification date
            const dateSpan = document.createElement('span');
            dateSpan.style.float = 'right';
            dateSpan.style.color = '#666';
            dateSpan.style.fontSize = '0.9em';
            dateSpan.textContent = file.modified;
            
            li.appendChild(a);
            li.appendChild(dateSpan);
            container.appendChild(li);
        });
        
    } catch (error) {
        console.error('Error loading docs files:', error);
        container.innerHTML = '<li style="color: red;">Error loading documentation files</li>';
    }
}

async function loadMarkdownFile(filename, title) {
    const content = document.getElementById('markdownContent');
    const docsList = document.getElementById('docsList');
    const backButton = document.getElementById('backButton');
    const pageTitle = document.getElementById('page-title');
    
    try {
        const response = await fetch(filename);
        const markdown = await response.text();
        
        content.innerHTML = marked.parse(markdown);
        
        docsList.style.display = 'none';
        content.style.display = 'block';
        backButton.style.display = 'inline-block';
        pageTitle.textContent = `📚 ${title}`;
        
    } catch (error) {
        console.error('Error loading markdown file:', error);
        content.innerHTML = '<p style="color: red;">Error loading markdown file</p>';
        content.style.display = 'block';
        docsList.style.display = 'none';
        backButton.style.display = 'inline-block';
    }
}

function showDocsList() {
    const content = document.getElementById('markdownContent');
    const docsList = document.getElementById('docsList');
    const backButton = document.getElementById('backButton');
    const pageTitle = document.getElementById('page-title');
    
    content.style.display = 'none';
    docsList.style.display = 'block';
    backButton.style.display = 'none';
    pageTitle.textContent = '📚 Documentation';
}

// Load docs files when page loads
document.addEventListener('DOMContentLoaded', loadDocsFiles);