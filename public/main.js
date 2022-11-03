let data1 =
    {
        "cars": {
            "Nissan": [{
                    "model": "Sentra",
                    "doors": 4
                },
                {
                    "model": "Maxima",
                    "doors": 4
                },
                {
                    "model": "Skyline",
                    "doors": 2
                }
            ],
            "Ford": [{
                    "model": "Taurus",
                    "doors": 4
                },
                {
                    "model": "Escort",
                    "doors": 4
                }
            ]
        }
    }

sessionStorage.setItem("key", JSON.stringify(data1));

function obtenerClientes(){
    let xhr = new XMLHttpRequest();
    xhr.open("GET", "/obtener-clientes", true);
    xhr.send();
    xhr.onreadystatechange = function() {
        if (this.readyState != 4) return;
        if (this.status == 200) {
            let data = JSON.parse(this.responseText)
            return data;
        }
      }
}

function filtrar(){
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/filtrar", true);
    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");

    let data = {
        "fecha_inicio": document.getElementById("fecha_inicio").value,
        "fecha_fin": document.getElementById("fecha_fin").value
    };

    xhr.send(JSON.stringify(data));
    xhr.onreadystatechange = function() {
        if(this.readyState != 4) return;
        if(this.status == 200){
            let data = JSON.parse(this.responseText)
            renderTable(data)
        }
    }
    console.log(JSON.parse(sessionStorage.getItem("key")))
}

function renderTable(data){
    let render = document.getElementById("tabla")
    let table = `<table>
    <tr>
      <th>Fecha Semana</th>
      <th>Cliente</th>
      <th>Producto</th>
      <th>Cantidad</th>
    </tr>`

    data.forEach(element => {
        table = table + 
        `<tr>
            <td>${element["Fecha Semana"]}</td>
            <td>${element["Cliente"]}</td>
            <td>${element["Producto"]}</td>
            <td>${element["Cantidad Total"]}</td>
        </tr>`
    });

    table = table + `</table>`
    render.innerHTML = table
    console.log(data[0])
}