
// On page load....


$(document).ready(function () {

    $('.date-time-input').attr('type', 'datetime');
    fetchDashboardItems();
    fetchWebsiteItems();

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





