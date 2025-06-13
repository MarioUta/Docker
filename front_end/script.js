//@ts-check

import Graph from "graphology";
import Sigma from "sigma";

function nxToGraphology(nxJson) {
    return {
        nodes: nxJson.nodes.map(n => {
            const { id, viz, ...rest } = n;
            const color = viz?.color ? { color: `rgba(${viz.color.r},${viz.color.g},${viz.color.b},${viz.color.a})` } : {};
            return {
                key: id,
                attributes: {
                    ...rest,
                    ...color  // inject flat color attribute
                }
            };
        }),
        edges: nxJson.links.map(l => {
            const { source, target, viz, ...rest } = l;
            const color = viz?.color ? { color: `rgba(${viz.color.r},${viz.color.g},${viz.color.b},${viz.color.a})` } : {};
            return {
                source,
                target,
                attributes: {
                    ...rest,
                    ...color
                }
            };
        })
    };
}

let mainGraph = ""

function createGraph(graph_json) {
    const fixedGraphJson = nxToGraphology(graph_json);
    //@ts-ignore
    const graph = Graph.from(fixedGraphJson);
    const container = document.getElementById('graph-container');

    //@ts-ignore
    container.innerHTML = '';

    let hoveredNode = null;
    let clickedNode = null;
    console.log(graph)

    //@ts-ignore
    const renderer = new Sigma(graph, container, {
        renderEdgeLabels: false,

        nodeReducer(node, data) {
            if (clickedNode) {
                const isVisible = node === clickedNode || graph.areNeighbors(node, clickedNode);
                return {
                    ...data,
                    hidden: !isVisible,
                    forceLabel: isVisible,
                };
            }

            if (hoveredNode) {
                const isNeighbor = node === hoveredNode || graph.areNeighbors(node, hoveredNode);
                return {
                    ...data,
                    //color: isNeighbor ? data.color : applyOpacity(data.color || '#ccc', 0.1),
                };
            }

            return { ...data };
        },

        edgeReducer(edge, data) {
            if (clickedNode) {
                const [source, target] = graph.extremities(edge);
                const isVisible = source === clickedNode || target === clickedNode;
                return {
                    ...data,
                    hidden: !isVisible,
                };
            }

            if (hoveredNode) {
                const [source, target] = graph.extremities(edge);
                const isNeighbor = source === hoveredNode || target === hoveredNode;
                return {
                    ...data,
                    color: applyOpacity(data.color || '#aaa', isNeighbor ? 0.6 : 0.05),
                    size: isNeighbor ? (data.size || 5) + 1 : data.size || 1,
                };
            }

            return { ...data };
        }
    });

    // Hover behavior
    renderer.on("enterNode", ({ node }) => {
        if (!clickedNode) {
            hoveredNode = node;
            renderer.refresh();
        }
    });

    renderer.on("leaveNode", () => {
        if (!clickedNode) {
            hoveredNode = null;
            renderer.refresh();
        }
    });

    // Click behavior
    renderer.on("clickNode", ({ node }) => {
        clickedNode = node;
        hoveredNode = null;
        renderer.refresh();
        getPapers(node);

        //@ts-ignore
        const bsOffcanvas = bootstrap?.Offcanvas || window.bootstrap?.Offcanvas;

        const offcanvas = new bsOffcanvas(document.getElementById('authorSidebar'));
        offcanvas.show();
    });

    renderer.on("clickStage", () => {
        clickedNode = null;
        hoveredNode = null;
        renderer.refresh();
        const authorDataContainer = document.getElementById('author-data-list')
        //@ts-ignore
        authorDataContainer.innerHTML = ''
    });

    // Helper
    function applyOpacity(color, opacity) {
        if (!color) return `rgba(200,200,200,${opacity})`;
        if (color.startsWith("rgba")) {
            return color.replace(/rgba\(([^)]+),[^)]+\)/, `rgba($1,${opacity})`);
        } else if (color.startsWith("rgb")) {
            return color.replace(/rgb\(([^)]+)\)/, `rgba($1,${opacity})`);
        } else if (color.startsWith("#")) {
            const bigint = parseInt(color.slice(1), 16);
            const r = (bigint >> 16) & 255;
            const g = (bigint >> 8) & 255;
            const b = bigint & 255;
            return `rgba(${r},${g},${b},${opacity})`;
        }
        return color;
    }
}

function getPapers(authorID) {
    fetch('http://localhost:3000/papers', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ authorID: authorID })
    }).then(response => response.json())
        .then(papers => {
            const authorDataContainer = document.getElementById('author-data-list');
            const authorDataList = document.createElement("ol");
            //@ts-ignore
            authorDataContainer.innerHTML = "";
            console.log(papers);

            for (let i = 0; i < papers.length; i++) {
                const listElement = document.createElement('li');
                const paperTitle = document.createElement('a');
                paperTitle.innerHTML = papers[i].title;
                listElement.appendChild(paperTitle);
                authorDataList.appendChild(listElement);
            }

            authorDataContainer?.append(authorDataList);

        });
}


function searchKeyword(keyword) {
    fetch('http://localhost:3000/send', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ keyword: keyword }),
    })
        .then(response => response.json())
        .then(gexfText => {
            mainGraph = gexfText.graph
            createGraph(mainGraph);
            const authors = gexfText.authors.author_names;
            const authorGraphs = gexfText.authors.author_graphs
            const papers = gexfText.papers;
            const authorListContainer = document.getElementById('authors-list');
            const papersListContainer = document.getElementById('papers-list');
            //@ts-ignore
            authorListContainer.innerHTML = '';
            //@ts-ignore
            papersListContainer.innerHTML = '';
            const authorsList = document.createElement("ol");
            for (let i = 0; i < authors.length; i++) {
                let list_item = document.createElement("li");
                let author = document.createElement("a");
                author.innerHTML = authors[i];
                author.href = "#";
                author.style.cursor = "pointer";

                // Add click handler if needed
                author.onclick = function (e) {
                    e.preventDefault();
                    console.log("Author clicked:", authors[i]);
                    console.log(authorGraphs[i])
                    createGraph(authorGraphs[i]);
                };

                list_item.appendChild(author);
                authorsList.appendChild(list_item);

            }
            authorListContainer?.appendChild(authorsList);

            const papersList = document.createElement("ol");
            for (let i = 0; i < papers.length; i++) {
                let paper = document.createElement("li");
                paper.innerHTML = papers[i];
                papersList.appendChild(paper);
            }
            papersListContainer?.appendChild(papersList);

        })
        .catch(error => console.error('Error:', error));
}

function searchAuthor(keyword) {
    fetch('http://localhost:3000/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ keyword: keyword }),
    })
        .then(response => response.json())
        .then(authorData => {
            const authorNames = authorData.author_names;
            const authorGraphs = authorData.author_graphs
            const authorListContainer = document.getElementById('authors-search-list');
            //@ts-ignore
            authorListContainer.innerHTML = '';
            const authorsList = document.createElement("ol");
            for (let i = 0; i < authorNames.length; i++) {
                let list_item = document.createElement("li");
                let author = document.createElement("a");
                author.innerHTML = authorNames[i];
                author.href = "#";
                author.style.cursor = "pointer";

                // Add click handler if needed
                author.onclick = function (e) {
                    e.preventDefault();
                    console.log("Author clicked:", authorNames[i]);
                    console.log(authorGraphs[i])
                    createGraph(authorGraphs[i]);
                };

                list_item.appendChild(author);
                authorsList.appendChild(list_item);
            }
            authorListContainer?.appendChild(authorsList);
        })
        .catch(error => console.error('Error:', error));

}

function authorSearch() {
    const graphContainer = document.getElementById('graph-container');
    const topicForm = document.getElementById("searchForm");
    const topicResults = document.getElementById("topic-results");
    const authorsList = document.getElementById("authors-list");
    const papersList = document.getElementById("papers-list");
    const resetButton = document.getElementById('reset');
    //@ts-ignore
    graphContainer.innerHTML = "";
    //@ts-ignore
    resetButton.style.display = "none";
    //@ts-ignore
    topicForm.style.display = "none";
    //@ts-ignore
    topicResults.style.display = "none";
    //@ts-ignore
    authorsList.style.display = "none";
    //@ts-ignore
    authorsList.innerHTML = "";
    //@ts-ignore
    papersList.style.display = "none";
    //@ts-ignore    
    papersList.innerHTML = "";


    const searchAuthor = document.getElementById("searchAuthor");
    const authorResults = document.getElementById("author-results");
    const authorsSearchList = document.getElementById("authors-search-list");


    //@ts-ignore
    searchAuthor.style.display = "block"
    //@ts-ignore
    authorResults.style.display = "block"
    //@ts-ignore
    authorsSearchList.style.display = "block"

}


function topicSearch() {
    const graphContainer = document.getElementById('graph-container');
    const topicForm = document.getElementById("searchForm");
    const topicResults = document.getElementById("topic-results");
    const authorsList = document.getElementById("authors-list");
    const papersList = document.getElementById("papers-list");
    const resetButton = document.getElementById('reset');

    //@ts-ignore
    graphContainer.innerHTML = "";
    //@ts-ignore
    resetButton.style.display = "block";
    //@ts-ignore
    topicForm.style.display = "block";
    //@ts-ignore
    topicResults.style.display = "block";
    //@ts-ignore
    authorsList.style.display = "block";
    //@ts-ignore
    papersList.style.display = "block";
    //@ts-ignore

    const searchAuthor = document.getElementById("searchAuthor");
    const authorResults = document.getElementById("author-results");
    const authorsSearchList = document.getElementById("authors-search-list");

    //@ts-ignore
    searchAuthor.style.display = "none"
    //@ts-ignore
    authorResults.style.display = "none"
    //@ts-ignore
    authorsSearchList.style.display = "none"
    //@ts-ignore
    authorsSearchList.innerHTML = "";

}

function main() {
    console.log('main')
    topicSearch()
    document.getElementById('searchForm')?.addEventListener('submit', function (e) {
        e.preventDefault();
        // @ts-ignore
        const keyword = document.getElementById('searchInput').value;
        searchKeyword("'" + keyword + "'");
    })
    document.getElementById('reset')?.addEventListener('click', function (e) {
        e.preventDefault();
        const authorDataContainer = document.getElementById('author-data-list')
        //@ts-ignore
        authorDataContainer.innerHTML = ''
        createGraph(mainGraph)
    })
    document.getElementById('searchAuthor')?.addEventListener('submit', function (e) {
        e.preventDefault()
        // @ts-ignore
        const keyword = document.getElementById('searchAuthorInput').value;
        searchAuthor("'" + keyword + "'")
    })

    document.getElementById('switchSearch')?.addEventListener('change', function () {
        const authorDataContainer = document.getElementById('author-data-list')
        //@ts-ignore
        authorDataContainer.innerHTML = ''
        //@ts-ignore
        if (this.checked) {
            console.log("Checkbox is checked!");
            // Call your function here, e.g.:
            authorSearch()
        } else {
            console.log("Checkbox is unchecked!");
            // Call another function, e.g.:
            topicSearch()
        }
    });
}

main()