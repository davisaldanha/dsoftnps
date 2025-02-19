function loadNPS(){
    fetch("/nps-data")
    .then(response => response.json())
    .then(data => {
        document.getElementById("nps-value").textContent = data.nps

        const ctx = document.getElementById("npsChart").getContext("2d")
        new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: ["Promotores", "Neutros", "Detratores"],
                datasets: [{
                    data: [data.promoters, data.passives, data.detractors],
                    backgroundColor: ["#e63946", "#f4a261", "#2a9d8f"]
                }]
            },
            options: {
                responsive: true,
                
            }
        })
    })
    .catch(error => console.error("Erro ao carregar dados do NPS: ", error))
}

function loadRadar(){
    fetch("/radar-data")
    .then(response => response.json())
    .then(data => {
        const ctx = document.getElementById("radarChart").getContext("2d")
        new Chart(ctx, {
            type: "radar",
            data: {
                labels: data.labels,
                datasets: [{
                    label: "Média das Notas por Pergunta",
                    data: data.values,
                    fill: true,
                    backgroundColor: "rgba(54, 162, 235, 0.2)",
                    borderColor: "rgba(54, 162, 235, 1)",
                    pointBackgroundColor: "rgba(54, 162, 235, 1)",
                }]
            },
            options: {
                responsive: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 10,
                        ticks: { stepSize: 1 }
                    }
                }
            }
        })
    })
}

function loadBars(){
    fetch('/bars-data')
    .then(response => response.json())
    .then(data => {
        const ctx = document.getElementById('barsChart').getContext('2d')

        const labels = Array.from({ length: 11 }, (_, i) => i) // Notas de 0 a 10
        const datasets = []

        questions = [
            "Recomendação", "Qualidade", "Atendimento", "Rapidez", "Preço", "Variedade", "Ambiente", "Busca", "Pagamento", "Custo-benefício"
         ]

        Object.keys(data).forEach((pergunta, index) => {
            datasets.push({
                label: `${questions[index]}`,
                data: labels.map(nota => data[pergunta][nota] || 0),
                backgroundColor: `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255}, 0.6)`,
                borderWidth: 1
            })
        })

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        })
    })
}