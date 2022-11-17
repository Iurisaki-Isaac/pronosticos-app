var selected_products = new Array();
var selected_customers = new Array();
var selected_sus_product = ""

obtenerClientes({})
obtenerProductos({})
setDefaultDates(12)

function obtenerClientes(data){
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/obtener-clientes", true);
    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify(data));
    xhr.onreadystatechange = function() {
        if (this.readyState != 4) return;
        if (this.status == 200) {
            let data = JSON.parse(this.responseText)
            //localStorage.setItem('clientes',data); //no se esta usando
            renderList(data,"customer-select","customer")
            return;            
        }
      }
}

function obtenerProductos(data){
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/obtener-productos", true);
    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify(data));
    xhr.onreadystatechange = function() {
        if (this.readyState != 4) return;
        if (this.status == 200) {
            let data = JSON.parse(this.responseText)
            //localStorage.setItem('productos',data); //no se esta usando
            renderList(data,"product-select","product")
            renderSustList(data)
            return;            
        }
      }
}

function filtrar(){
    let xhr = new XMLHttpRequest();
    let data = {
        "fecha_inicio": document.getElementById("fecha_inicio").value,
        "fecha_fin": document.getElementById("fecha_fin").value,
        "fecha_inicio_a": document.getElementById("fecha_inicio_a").value,
        "fecha_fin_a": document.getElementById("fecha_fin_a").value,
        "cliente": getSelectedValues("customer"),
        "producto": getSelectedValues("product"),
        "tasa": document.getElementById("tasa").value,
        "desperdicio": document.getElementById("desperdicio").value,
        "sustitucion": document.getElementById("sustitucion").value
    };
    if(verifyRequieredFields(data) == null){
        xhr.open("POST", "/filtrar", true);
        xhr.setRequestHeader("Accept", "application/json");
        xhr.setRequestHeader("Content-Type", "application/json");    
        xhr.send(JSON.stringify(data));
        xhr.onreadystatechange = function() {
            if(this.readyState != 4) return;
            if(this.status == 200){
                let data = JSON.parse(this.responseText)      
                if(data.response.length > 0){
                    renderTable(data.response)
                    renderSummaryTable(data.summary)
                }
                else renderNoResults()             
            }
        }
    }
    else{
        alert(verifyRequieredFields(data))
    }
}

function verifyRequieredFields(data){
    if(data['producto'].length < 1) return 'Selecciona un(a) producto'
    if(data['fecha_inicio'] == '') return 'Selecciona un(a) fecha de incio de pronostico'
    if(data['fecha_fin'] == '') return 'Selecciona un(a) fecha de fin de pronostico'
    if(data['producto'].length > 1 && data['sustitucion'] != '') return 'Solo puedes usar el campo sustitucion con un maximo de un producto'
    return null
}

function getSelectedValues(id) {
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
    let preselected_elements = []
    if(id == 'customer') preselected_elements = selected_customers
    if(id == 'product') preselected_elements = selected_products
    let render = document.getElementById(element_id)
    let list = `<select id="${id}" class="js-states form-control" onchange="updateList('${id}')" multiple>`
    data.forEach(element => {
        if(preselected_elements.includes(element)) list = list + `<option selected>${element}</option>`
        else{
            list = list + `<option>${element}</option>`
        }        
    })
    list = list + `</select>`
    render.innerHTML = list

    $(`#${id}`).select2({
        allowClear: true,
        width: "35vw",
        placeholder: ""
    }); 
}

function updateList(list){
    if(list == 'product'){        
        selected_customers = getSelectedValues("customer")
        obtenerClientes({'producto' : getSelectedValues("product")})
    }
    if(list == 'customer'){
        selected_sus_product = document.getElementById("sustitucion").value
        selected_products = getSelectedValues("product")
        obtenerProductos({'cliente' : getSelectedValues("customer")})
    }
}

function renderSustList(data){
    let render = document.getElementById("sust_input_container")
    let list = `<label for="sustitucion">
        Sustituci&oacute;n
            <div class="tooltip">
                    <i class="fa-solid fa-circle-question"></i>
                    <span class="tooltiptext">Puede seleccionar un producto en este campo para indicar que es una versi&oacute;n anterior del producto a pronosticar.</span>
            </div>
        </label>
        <div class="inputs-ex"><select class="js-states form-control input-ex" id="sustitucion"></div>`
    data.forEach(element => {
        list = list + `<option>${element}</option>`
    })
    list = list + `</select>`
    render.innerHTML = list
    if(selected_sus_product != "") document.getElementById("sustitucion").value = selected_sus_product
    else document.getElementById("sustitucion").selectedIndex = -1;
 

    $(`#sustitucion`).select2({
        allowClear: true,
        width: "100%",
        placeholder: ""
    });
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
            <td>${element["Nombre"]}</td>
            <td>${element["Producto"]}</td>
            <td>${element['Cantidad Pronostico']}</td>
        </tr>`
    });

    table = table + `</table>`
    render.innerHTML = table
}

function renderSummaryTable(data){
    let render = document.getElementById("tabla-resumen")
    let table = `<table><tr><th colspan="3">Resumen</th></tr>
    <tr>
      <th>Producto</th>
      <th>Promedio semanal pronosticado</th>
      <th>Total pronosticado</th>
    </tr>`

    data.forEach(element => {        
        table = table + 
        `<tr>
            <td>${element["Producto"]}</td>        
            <td>${element["Promedio semana"]}</td>
            <td>${element["Total"]}</td>        
        </tr>`
    });

    table = table + `</table>`
    render.innerHTML = table
}

function renderNoResults(){
    let render = document.getElementById("tabla")
    let render_resumen = document.getElementById("tabla-resumen")
    render.innerHTML = `<h2>No hay resultados.</h2>`
    render_resumen.innerHTML = ''
}

function fixClearButton(){
    let buttons = document.getElementsByClassName("select2-selection__clear")
    buttons[0].setAttribute('id', 'Introduction_ 1')
}

function setDefaultDates(months_back_in_time){
    let today = new Date()
    let init_date = new Date()
    init_date.setMonth(init_date.getMonth() - months_back_in_time)
    document.getElementById("fecha_fin_a").valueAsDate = today
    document.getElementById("fecha_inicio_a").valueAsDate = init_date
}