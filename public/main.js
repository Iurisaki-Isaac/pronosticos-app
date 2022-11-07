obtenerClientes()
obtenerProductos()

function obtenerClientes(){
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/obtener-clientes", true);
    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send();
    xhr.onreadystatechange = function() {
        if (this.readyState != 4) return;
        if (this.status == 200) {
            let data = JSON.parse(this.responseText)
            localStorage.setItem('clientes',data);
            renderList(data,"customer-select","customer")
            return;            
        }
      }
}

function obtenerProductos(){
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/obtener-productos", true);
    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send();
    xhr.onreadystatechange = function() {
        if (this.readyState != 4) return;
        if (this.status == 200) {
            let data = JSON.parse(this.responseText)
            localStorage.setItem('productos',data);
            renderList(data,"product-select","product")
            return;            
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
        "fecha_fin": document.getElementById("fecha_fin").value,
        "cliente": getSelectValues("customer"),
        "producto": getSelectValues("product")
    };

    xhr.send(JSON.stringify(data));
    xhr.onreadystatechange = function() {
        if(this.readyState != 4) return;
        if(this.status == 200){
            let data = JSON.parse(this.responseText)
            renderTable(data)
        }
    }
}

function getSelectValues(id) {
    let select = document.getElementById(id)
    let result = [];
    let options = select && select.options;
    let opt;
  
    for (let i=0, iLen=options.length; i<iLen; i++) {
      opt = options[i];
  
      if (opt.selected) {
        result.push(opt.value || opt.text);
      }
    }
    return result;
  }

function renderList(data,element_id,id){
    let render = document.getElementById(element_id)
    let list = `<select name="${id}" id="${id}" class="js-example-basic-multiple" multiple="multiple">`
    data.forEach(element => {
        list = list + `<option>${element}</option>`
    })
    list = list + `</select>`
    render.innerHTML = list
}

function renderTable(data){
    let render = document.getElementById("tabla")
    let table = `<table>
    <tr>
      <th>Tipo</th>
      <th>Fecha Semana</th>
      <th>Cliente</th>
      <th>Nombre</th>
      <th>Producto</th>
      <th>Cantidad</th>
    </tr>`

    data.forEach(element => {
        let cantidad = ""
        let tipo = ""
        if(element["Cantidad Total"] == null){
            cantidad = element["P. Semana"]
            tipo = "PRONOSTICO"
        }
        else{
            cantidad = element["Cantidad Total"]
            tipo = "FACTURA"
        }

        table = table + 
        `<tr>
            <td>${tipo}</td>
            <td>${element["Fecha Semana"]}</td>
            <td>${element["Cliente"]}</td>
            <td>${element["Nombre"]}</td>
            <td>${element["Producto"]}</td>
            <td>${cantidad}</td>
        </tr>`
    });

    table = table + `</table>`
    render.innerHTML = table
}

//buscador en seleccion multiple
$(document).ready(function() {
    $('.js-example-basic-multiple').select2();
});