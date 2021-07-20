const main = () => {
  let ctx = document.getElementById('myChart').getContext('2d');

  const { labels, data_sgd, total_deposited_sgd, portfolio_sgd } = data;

  const config = {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Profit (SGD)',
          borderColor: '#e76f51',
          borderWidth: 1,
          radius: 0,
          data: data_sgd,
        },
        {
          label: 'Total Deposited (SGD)',
          borderColor: '#2a9d8f',
          borderWidth: 1,
          radius: 0,
          data: total_deposited_sgd,
        },
        {
          label: 'Portfolio Value (SGD)',
          borderColor: '#f4a261',
          borderWidth: 1,
          radius: 0,
          data: portfolio_sgd,
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
          text: 'Profit Over Time',
        },
      },
    },
  };

  let myChart = new Chart(ctx, config);
};

main();
