

function addClass(status) {
    status = parseInt(status)
    if (!status) {
        return 'class="passed"'
    }else {
        return 'class="failed"'
    }
}


function parseL3BasicTestResult (result, l3Status, ipProtocol) {
    let l3BasicTestResult = `
    <input type="hidden" id="l3-status-${ipProtocol}" l3-status-${ipProtocol}=${l3Status}>
    <input type="hidden" id="ip-protocol-${ipProtocol}" ip-protocol-${ipProtocol}=${ipProtocol}>
        <strong>
            <div class="result">
                <span ${addClass(l3Status)}><pre>${result}</pre></span></strong>
            </div><br>`
    return l3BasicTestResult
}

function parseL3AdvancedTestResult(result, bgpStatus=null, peeringPolicy, ipProtocol) {
    let lastError = result.last_error;
    let l3AdvancedTestResult;
    if (peeringPolicy == 'open') {
        l3AdvancedTestResult = `
        <input type="hidden" id=bgp-status-${ipProtocol} bgp-status-${ipProtocol}=${bgpStatus}>
            <div class="result">
                <strong>
                    BGP State: <span ${addClass(bgpStatus)}>${result.bgp_state}</span><hr>`

                    if (lastError){
                    l3AdvancedTestResult += `Last Error: <span ${addClass(bgpStatus)}>${lastError}</span><hr>`
                    }
        
                    l3AdvancedTestResult += `
                    Since: ${result.since}<hr>
                    Received Routes: ${result.imported}<hr>
                    Advertized Routes: ${result.exported}<hr>
                </strong>
            </div><br><br>`
        return l3AdvancedTestResult
    }else {
        l3AdvancedTestResult = `
        <div class="result">
            <strong>
                <p>${result}</p>
            </strong>
        </div><br><br>`
        return l3AdvancedTestResult
    }
}

function l3BasicTest(ipProtocol) {
    let l2Status = $("#l2-status").attr("l2-status");
    l2Status = parseInt(l2Status)
    if (!l2Status) {  
        scrollToElement(`#l3-test-result-${ipProtocol}`)
        $(`#get-l3-status-${ipProtocol}`).css("display", "block");
        let url = $("#l3-test-url").attr("l3-test-url");
        $(`.dynamic-heading-${ipProtocol}`).append( `L3 TEST RESULTS (${ipProtocol.toUpperCase()})`)
            
            $.ajax({
                type : "GET", 
                url : url,
                data: {
                    ipProtocol: ipProtocol,
                    dataType: "json",
                
                },
                
                success: function(data){
                    $(`#get-l3-status-${ipProtocol}`).hide();
                    $(`#l3-test-result-${ipProtocol}`).html(
                        parseL3BasicTestResult(data.output,
                                            data.l3_status,
                                            data.ip_protocol
                                            )
                        );
                        l3AdvancedTest(ipProtocol)
                        
                    
                },
                       
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    $('#bgp_status').html(`<p class="text-danger">&emsp;&emsp;&emsp;${errorThrown}</p>`)
                    $('#get-l3-status').hide();
                
                }      
            });
    }

}


$(document).ready(function () { 
    $('.date-time-input').attr('type', 'datetime');
    fetchDashboardItems();
    fetchWebsiteItems();
    var t = $("#all-behind, #asn-table, #other-asns, #naija-asns, #notdirectly, #members, #notinixpn, #indirectly-connected").DataTable({
        "dom": 't',
        columnDefs: [
          { searchable: false, orderable: false, targets: 0},
          
        ],
        pageLength: 5000,
        lengthMenu: [10, 50, 100, 500, 1000],
        order: [[1, 'asc']],
        
     });
     t.on('order.dt search.dt', function () {
        let i = 1;
 
        t.cells(null, 0, { search: 'applied', order: 'applied' }).every(function (cell) {
            this.data(i++);
        });
    }).draw();

    var tt = $("#peers-table").DataTable({
        "dom": 'tt',
        columnDefs: [
            { "orderData":[ 7 ],   "targets": [ 6 ] },
            {
                    "targets": [ 7 ],
                    "visible": false,
                    "searchable": false
                },
          
        ],
        pageLength: 500,
        lengthMenu: [10, 50, 100, 500, 1000],
        order: [[1, 'asc']],
        
     });
     tt.on('order.dt search.dt', function () {
        let i = 1;
 
        tt.cells(null, 0, { search: 'applied', order: 'applied' }).every(function (cell) {
            this.data(i++);
        });
    }).draw();

});


function scrollToElement(id_or_class){
    $('html, body').animate({
        scrollTop: $(id_or_class).offset().top
    }, 1000);
}


$(".adv-l3-test").click(function(){
    let ipProtocol = $(this).val();
    $(this).prop("disabled",true);
    l3BasicTest(ipProtocol);
});

$(".get-logs").click(function(){
    fetchLogs()
});

// Toggle filter form on mobile display
$(".hidden-filter-icon").click(function(){
    $(".tty").toggle();
});


$('.reset-button').on('click', function(){
    $("select").each(function() { this.selectedIndex = 0 });
    $(".numberinput").val("");
    $(".dateinput").val("");
    $(".submit-button").click();
});



const options = {
    scales: {
      x: {
          grid: {
              display: true
          },
          ticks: {
              font: {
                  family: 'Raleway', // Your font family
                  size: 16,
                  weight: 900
              },
          },
      },
        y: {
            beginAtZero: true,
            ticks: {
              font: {
                  family: 'Raleway', // Your font family
                  size: 16,
                  weight: 900
              },
          },
            
        }
    },
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: true,
        text: 'TOP 10 MEMBERS WITH MOST ASNS',
        position: 'top',
        align: 'center',
        font: {
            weight: 900,
            size: 18
        } 
    }
    }
}


function options_II(title) {
    let options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    font: {
                        weight: 'bold',
                        size: 12
                    },
                    boxHeight: 10,
                    boxWidth: 10,
                    textAlign: 'left'
                },
                position: 'right',
              
            },
            title: {
                display: true,
                text: title,
                position: 'top',
                align: 'left',
                font: {
                    weight: 900,
                    size: 18
                } 
            }
          }
    }

    return options

}


function fetchDashboardItems () {
    let dashboard = $("#dashboard").attr("data-dashboard");
    if (dashboard == "yes") {
        let url = document.location.href
        $.ajax({ 
            url: url,

            success: function (data) { 
                let uche = 300000
                $('.naijaIxpn').append(data.naija_dc_idc.toLocaleString())
                $('.allNaija').append(data.naija.toLocaleString())
                $('.totalASNS').append(data.total_no_of_asns.toLocaleString())
                $('.notIxpn').append(data.naija_not_at_ixpn.toLocaleString())
                $('#caption').append(data.caption)

                let othersLabels = []
                let othersData = []
                let countryLabelsDC = []
                let countryDataDC = []
                let countryLabelsIDC = []
                let countryDataIDC = []
                let registryLabelsDC = []
                let registryDataIDC = []
                let registryLabelsIDC = []
                let registryDataDC = []

                for (let i = 0; i < data.top_10_asns.length; i++) {
                    othersLabels.push(`${data.top_10_asns[i].member__member} (${data.top_10_asns[i].c})`)
                    othersData.push(data.top_10_asns[i].c)
                }

                for (let i = 0; i < data.top_5_countries_dc.length; i++) {
                    countryLabelsDC.push(`${data.top_5_countries_dc[i].country} (${data.top_5_countries_dc[i].c})`)
                    countryDataDC.push(data.top_5_countries_dc[i].c)
                }

                for (let i = 0; i < data.top_5_countries_idc.length; i++) {
                    countryLabelsIDC.push(`${data.top_5_countries_idc[i].country} (${data.top_5_countries_idc[i].c})`)
                    countryDataIDC.push(data.top_5_countries_idc[i].c)
                }

                for (let i = 0; i < data.top_5_registries_dc.length; i++) {
                    registryLabelsDC.push(`${data.top_5_registries_dc[i].registry} (${data.top_5_registries_dc[i].c})                       `)
                    registryDataDC.push(data.top_5_registries_dc[i].c)
                }

                for (let i = 0; i < data.top_5_registries_idc.length; i++) {
                    registryLabelsIDC.push(`${data.top_5_registries_idc[i].registry} (${data.top_5_registries_idc[i].c})                      `)
                    registryDataIDC.push(data.top_5_registries_idc[i].c)
                }

                let openPeeringPolicy = data.open_peering_policy;
                let selectivePeeringPolicy = data.selective_peering_policy;
                let directlyConnectedASNS = data.directly_connected_asns;
                let indirectlyConnectedASNS = data.indirectly_connected_asns;

                let policyCtx = document.getElementById('policyChart').getContext('2d');
                let connectionCtx = document.getElementById('connectionChart').getContext('2d');
                let countryDCCtx = document.getElementById('countryDCChart').getContext('2d');
                let countryIDCCtx = document.getElementById('countryIDCChart').getContext('2d');
                let registryDCCtx = document.getElementById('registryDCChart').getContext('2d');
                let registryIDCCtx = document.getElementById('registryIDCChart').getContext('2d');
                let othersCtx = document.getElementById('othersChart').getContext('2d');
        
                let othersChart = new Chart(othersCtx, {
                    type: 'bar',
                    data: {
                        labels: othersLabels,
                        datasets: [{
                            data: othersData,
                            backgroundColor: [
                              'rgba(30, 130, 76, 1)',
                            ],
                            borderColor: [
                              'rgba(30, 130, 76, 1)',
                            ],
                            borderWidth: 1
                        }]
                    },
                    options: options,
                });
        

                let policyChart = new Chart(policyCtx, {
                    type: 'doughnut',
                    data: {
                        labels: [`OPEN: ${openPeeringPolicy}                    `, `SELECTIVE: ${selectivePeeringPolicy}                       `],
                        datasets: [{
                            data: [openPeeringPolicy, selectivePeeringPolicy],
                            backgroundColor: [
                                '#008000',
                                '#FFA500',
                            ],
                            borderColor: [
                                '#008000',
                                '#FFA500',
                            ],
                            borderWidth: 1
                        }]
                    },
                    options : options_II('DIRECTLY CONNECTED ASNS BY PEERING POLICY')
                });


                let connectionChart = new Chart(connectionCtx, {
                    type: 'doughnut',
                    data: {
                        labels: [`DIRECTLY CONNECTED: ${directlyConnectedASNS}`, `INDIRECTLY CONNECTED: ${indirectlyConnectedASNS}`],
                        datasets: [{
                            data: [directlyConnectedASNS, indirectlyConnectedASNS],
                            backgroundColor: [
                              '#406D00',
                              '#DAA520',
                            ],
                            borderWidth: 1
                        }]
                    },
                    options : options_II('ALL ASNS BY CONNECTION')  
                });


                let countryDCChart = new Chart(countryDCCtx, {
                    type: 'pie',
                    data: {
                        labels: countryLabelsDC,
                        datasets: [{
                            data: countryDataDC,
                            backgroundColor: [
                              '#008000',
                              '#0000FF',
                              '#4B0082',
                              '#C71585',
                              '#696969'
                            ],
                            borderWidth: 1
                        }]
                    },
                    options : options_II('DIRECTLY CONNECTED ASNS TOP 5 COUNTRIES')
                });


                let countryIDCChart = new Chart(countryIDCCtx, {
                    type: 'pie',
                    data: {
                        labels: countryLabelsIDC,
                        datasets: [{
                            data: countryDataIDC,
                            backgroundColor: [
                                '#008000',
                                '#0000FF',
                                '#4B0082',
                                '#C71585',
                                '#696969'
                            ],
                            borderWidth: 1
                        }]
                    },
                    options : options_II('INDIRECTLY CONNECTED ASNS TOP 5 COUNTRIES')  
                });


                let registryDCChart = new Chart(registryDCCtx, {
                    type: 'pie',
                    data: {
                        labels: registryLabelsDC,
                        datasets: [{
                            data: registryDataDC,
                            backgroundColor: [
                                '#6B8E23',
                                '#4169E1',
                                '#8A2BE2',
                                '#800000',
                                '#66CDAA',
                            ],
                            borderWidth: 1
                        }]
                    },
                    options :  options_II('DIRECTLY CONNECTED ASNS TOP 5 REGISTRIES') 
                });


                let registryIDCChart = new Chart(registryIDCCtx, {
                    type: 'pie',
                    data: {
                        labels: registryLabelsIDC,
                        datasets: [{
                            data: registryDataIDC,
                            backgroundColor: [
                                '#6B8E23',
                                '#4169E1',
                                '#8A2BE2',
                                '#800000',
                                '#66CDAA', 
                            ],
                            borderWidth: 1
                        }]
                    },
                    options :  options_II('INDIRECTLY CONNECTED ASNS TOP 5 REGISTRIES')   
                });
            }
        });
    }
}


function fetchWebsiteItems() {
    let dashboardweb = $("#dashboardweb").attr("data-dashboardweb");
    if (dashboardweb == "yes") {
        let url = document.location.href

        $.ajax({ 
            url: url,
      
            success: function (data) { 
                let openPeeringPolicy = data.open_peering_policy;
                let selectivePeeringPolicy = data.selective_peering_policy;
                let policyCtx = document.getElementById('policyChart').getContext('2d');
                let policyChart = new Chart(policyCtx, {
                    type: 'doughnut',
                    data: {
                        labels: [`OPEN: ${openPeeringPolicy}                    `, `SELECTIVE: ${selectivePeeringPolicy}                       `],
                        datasets: [{
                            data: [openPeeringPolicy, selectivePeeringPolicy],
                            backgroundColor: [
                                '#008000',
                                '#FFA500',
                            
                            ],
                            borderColor: [
                                '#008000',
                                '#FFA500',
                            
                            ],
                            borderWidth: 1
                        }]
                    },
                    options : options_II('DIRECTLY CONNECTED ASNS BY PEERING POLICY')
                });
            }
        });
    }
}


function parseGetPrefixesOutput(outputData, listOfTableTH=null, tableId=null, bgpPeer=null, infrastructure=null, pop=null, ipProtocol=null) {
    let getPrefixesResult;
    if (tableId) {
    const he_url = 'https://bgp.he.net/AS'
        getPrefixesResult = `<table class="table-sort table-arrows" id=${tableId}-${ipProtocol}><caption> 
                            ${ipProtocol.toUpperCase()} Prefixes receieved from  - ${bgpPeer} at ${pop}</caption><thead><tr>`
        getPrefixesResult += '<th>s/no</th>'
        listOfTableTH.forEach((item) => {
           getPrefixesResult += `<th>${item}</th>`
        });

        getPrefixesResult += '</tr></thead><tbody>'

        let sno = 0
        outputData.forEach(protocol => {
            sno ++
            getPrefixesResult += `<tr><td>${sno}</td>`
            listOfTableTH.forEach((item) => {
                let param = protocol[item]
                if (item == 'asn') {
                    getPrefixesResult += `<td><a href="${he_url}${param}" target="_blank" rel="noopener noreferrer">${param}</a></td>`
                }else if (item == 'bgp_state' && param == 'Established') {
                    getPrefixesResult += `<td><span class="green">${param}</span></td>`
                }else if (item == 'bgp_state') {
                    getPrefixesResult += `<td><span class="red">${param}</span></td>`
                }else if (item == 'imported' && param <= 3000 && param > 0) {
                    getPrefixesResult += `<td><span class="received-routes"><a href="#">${param}</a></span></td>`
                }else if (item == 'path') {
                    let paths = ''
                    param.forEach((path) => {
                        paths += `<a href="${he_url}${path}" target="_blank" rel="noopener noreferrer">${path}</a> `
                    })
                    getPrefixesResult += `<td>${paths}</td>`
                }else {
                    getPrefixesResult += `<td>${param}</td>` 
                }
            })
            getPrefixesResult += '</tr>'

            })

            getPrefixesResult += '</tbody></table><br><br><br>'

        return getPrefixesResult

        }else {
            getPrefixesResult += `<p>${outputData}</p>`
        }
        return getPrefixesResult;
    }

function parseGetLogsOutput(logs, listOfTableTH) {
    let getLogsResult;
    getLogsResult = `<table class="table-sort table-arrows" id="logs-table"><caption> 
                                 </caption><thead><tr>`
            getLogsResult += '<th>s/no</th>'
            listOfTableTH.forEach((item) => {
                getLogsResult += `<th>${item}</th>`
            });
    
            getLogsResult += '</tr></thead><tbody>'
    
            let sno = 0
            logs.forEach(log => {
                sno ++
                getLogsResult += '<tr><td>${sno}</td>'
                listOfTableTH.forEach((item) => {
                    let param = log[item]
                    
                    getLogsResult += `<td><pre>${param}</pre></td>` 
                    
                })
                getLogsResult += '</tr>'
    
                })
    
                getLogsResult += '</tbody></table><br><br><br>'
    
            return getLogsResult

        }
    
    


function getPrefixes(ipProtocol){
    let bgpStatus = $(`#bgp-status-${ipProtocol}`).attr(`bgp-status-${ipProtocol}`);
    bgpStatus = parseInt(bgpStatus)
    if (!bgpStatus) {
        $(`#get-prefixes-${ipProtocol}`).css("display", "block");
        scrollToElement(`#prefixes-${ipProtocol}`);
        let bgpPeer = $("#peer").attr("peer");
        let peerId = $("#peer-id").attr("peer-id");
        let url = $("#get-prefixes-url").attr("get-prefixes-url");
        let infrastructure = $("#infrastructure").attr("infrastructure");
        
        $.ajax({
            type : "GET", 
            url : url,
            data: {
                infrastructure: infrastructure,
                bgpPeer: bgpPeer,
                peerId: peerId,
                ipProtocol: ipProtocol,
                dataType: "json",
            
            },
            
            success: function(data){
                $(`#prefixes-${ipProtocol}`).html(
                    parseGetPrefixesOutput(
                        data.result,
                        data.table_header, 
                        data.table_id,
                        data.bgp_peer,
                        data.infrastructure,
                        data.pop,
                        ipProtocol
                        )
                    );
                var t = $(`#${data.table_id}`).DataTable({
                    "dom": 't',
                    columnDefs: [
                      { type: 'ip-address', targets: data.ip_col },
                      { searchable: false, orderable: false, targets: 0},
                      
                    ],
                    pageLength: 5000,
                    lengthMenu: [10, 50, 100, 500, 1000],
                    order: [[1, 'asc']],
                    
                });
                
                 t.on('order.dt search.dt', function () {
                    let i = 1;
             
                    t.cells(null, 0, { search: 'applied', order: 'applied' }).every(function (cell) {
                        this.data(i++);
                    });
                }).draw();
                $(`#get-prefixes-${ipProtocol}`).hide();
            },
                   
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                $(`#get-prefixes-${ipProtocol}`).hide();
                $(`#prefixes-${ipProtocol}`).html(`<p class="text-danger">&emsp;&emsp;&emsp;${errorThrown}</p>`)
            
            }      
        });
    }};



function l3AdvancedTest(ipProtocol) {
    console.log(ipProtocol)
    let l3Status = $(`#l3-status-${ipProtocol}`).attr(`l3-status-${ipProtocol}`);
    console.log(l3Status)
    let peeringPolicy = $("#pp").attr("pp");
    
    let bgpPeer = $("#peer").attr("peer");
    l3Status = parseInt(l3Status)
    if (!l3Status && peeringPolicy == 'open') {
        $(`#get-bgp-status-${ipProtocol}`).css("display", "block");
        let url = $("#bgp-status-url").attr("bgp-status-url");
        let infrastructure = $("#infrastructure").attr("infrastructure");
        
        $.ajax({
            type : "GET", 
            url : url,
            data: {
                infrastructure: infrastructure,
                bgpPeer: bgpPeer,
                ipProtocol: ipProtocol,
                dataType: "json",
            
            },
            
            success: function(data){
                let bgpStatus = parseInt(data.bgp_status)
                $(`#bgp-status-${ipProtocol}`).html(
                    parseL3AdvancedTestResult(
                        data.result, 
                        bgpStatus, 
                        peeringPolicy,
                        ipProtocol
                        )
                );
                $(`#get-bgp-status-${ipProtocol}`).hide();
                if (!bgpStatus) {
                    getPrefixes(ipProtocol)
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                $(`#bgp-status-${ipProtocol}`).html(`<p class="text-danger">&emsp;&emsp;&emsp;${errorThrown}</p>`)
            
            }      
        });

    }else if (!l3Status && peeringPolicy != 'open') {
        let result = `${bgpPeer}'s peering policy is ${peeringPolicy}, <br> therefore there is no BGP session with any of the route servers.`
        $(`#bgp-status-${ipProtocol}`).html(
            parseL3AdvancedTestResult(result, bgpStatus=1)
        );
    }
    };

function fetchLogs() {
            $('#fetch-logs').css("display", "block");
            let url = $("#fetch-logs-url").attr("fetch-logs-url");
            
            $.ajax({
                type : "GET", 
                url : url,
                data: {
                    dataType: "json"
                
                },
                
                success: function(data){
                    $('#fetch-logs-result').html(
                        parseGetLogsOutput(data.results, data.table_header)
                    );
                    var t = $("#logs-table").DataTable({
                        "dom": 't',
                        columnDefs: [
                          { searchable: false, orderable: false, targets: 0},
                          
                        ],
                        pageLength: 5000,
                        lengthMenu: [10, 50, 100, 500, 1000],
                        order: [[1, 'asc']],
                        
                    });
                    
                     t.on('order.dt search.dt', function () {
                        let i = 1;
                 
                        t.cells(null, 0, { search: 'applied', order: 'applied' }).every(function (cell) {
                            this.data(i++);
                        });
                    }).draw();
                    $('#fetch-logs').hide();
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    $('#bgp_status').html(`<p class="text-danger">&emsp;&emsp;&emsp;${errorThrown}</p>`)
                
                }      
            });

        };


// Overlay effect
$(".overly").on('click', function(){
    let asnId = $(this).attr('asn-id');
    $(`.modalbox-${asnId}`).css("display", "block");
});
$(".closebutton").on('click', function(){
    let asnId = $(this).attr('asn-id');
    $(`.modalbox-${asnId}`).hide();
});
