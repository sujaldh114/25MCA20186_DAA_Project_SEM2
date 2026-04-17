let grid = [];
let start = null;
let goals = [];

const size = 15;
const gridDiv = document.getElementById("grid");

// CREATE GRID
for (let i = 0; i < size; i++) {
    grid[i] = [];

    for (let j = 0; j < size; j++) {
        grid[i][j] = 1;

        let cell = document.createElement("div");
        cell.classList.add("cell");

        cell.addEventListener("click", () => handleClick(i, j, cell));

        gridDiv.appendChild(cell);
    }
}

function handleClick(i, j, cell) {

    // START
    if (!start) {
        start = [i, j];
        cell.classList.add("start");
    }

    // GOAL
    else if (!cell.classList.contains("goal") && !cell.classList.contains("traffic")) {
        goals.push([i, j]);
        cell.classList.add("goal");
    }

    // TRAFFIC
    else {
        grid[i][j] = 5;
        cell.classList.remove("goal");
        cell.classList.add("traffic");

        goals = goals.filter(g => !(g[0] === i && g[1] === j));
    }
}

function findRoute() {

    if (!start || goals.length === 0) {
        alert("Please select START and at least one GOAL");
        return;
    }

    let algo = document.getElementById("algo").value;

    fetch("/route", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ grid, start, goals, algo })
    })
    .then(res => res.json())
    .then(data => {

        clearPath();

        if (!data.path || data.path.length === 0) {
            document.getElementById("info").innerText =
                "⚠️ No path found (Possible in Hill Climbing)";
            return;
        }

        animatePath(data.path);

        document.getElementById("info").innerText =
            `Algorithm: ${algo.toUpperCase()} | Cost: ${data.cost}`;
    });
}

function animatePath(path) {
    const cells = document.querySelectorAll(".cell");

    path.forEach(([x,y], i) => {
        setTimeout(() => {
            let index = x * size + y;
            cells[index].classList.add("path");
        }, i * 40);
    });
}

function clearPath() {
    document.querySelectorAll(".cell").forEach(cell => {
        cell.classList.remove("path");
    });
}

function resetGrid() {
    location.reload();
}