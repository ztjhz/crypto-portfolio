const main = () => {
  let ctx = document.getElementById('myChart').getContext('2d');

  const {
    labels,
    data_sgd,
    total_deposited_sgd,
    net_deposit,
    portfolio_sgd,
    total_withdrawn_sgd,
  } = data;

  const config = {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Profit (SGD)',
          borderColor: '#264653',
          borderDash: [3, 3],
          borderWidth: 1,
          radius: 0,
          data: data_sgd,
          tension: 0.2,
        },
        {
          label: 'Total Deposited (SGD)',
          borderColor: '#2a9d8f',
          borderDash: [3, 3],
          borderWidth: 2,
          radius: 0,
          data: total_deposited_sgd,
        },
        {
          label: 'Total Withdrawn (SGD)',
          borderColor: '#e76f51',
          borderDash: [3, 3],
          borderWidth: 2,
          radius: 0,
          data: total_withdrawn_sgd,
        },
        {
          label: 'Net Deposit (SGD)',
          borderColor: '#2a9d8f',
          backgroundColor: 'rgba(42,157,143, 0.3)',
          fill: true,
          borderWidth: 2,
          radius: 0,
          data: net_deposit,
        },
        {
          label: 'Portfolio Value (SGD)',
          borderColor: '#e76f51',
          borderWidth: 1,
          radius: 0,
          data: portfolio_sgd,
          tension: 0.2,
        },
      ],
    },
    options: {
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: 'Portfolio',
        },
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: 'Time',
          },
        },
      },
    },
  };

  let myChart = new Chart(ctx, config);
};

main();
