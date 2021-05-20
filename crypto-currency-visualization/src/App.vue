<template>
  <div id="app" class="container">
    <div class="row mt-5" v-if="arrRate.length > 0">
      <div class="col">
        <h2>Cryptos</h2>
        <line-chart
          :chartData="arrRate"
          :options="chartOptions"
          :chartColors="rateColors"
          label="Crypto Price"
        >
        </line-chart>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import moment from "moment";
import LineChart from "./components/LineChart";
import numeral from "numeral";
export default {
  name: "App",
  components: {
    LineChart,
  },
  data() {
    return {
      arrRate: [],
      rateColors: {
        borderColor: "#000000",
        pointBorderColor: "#ffffff",
        pointBackgroundColor: "#ff2300",
        backgroundColor: "#00dcff",
      },
      arrRate2: [],
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
      },
    };
  },
  async created() {
    const { data } = await axios.get(
      "https://api.nomics.com/v1/exchange-rates/history?key=90ca6f8d455c8771f6189cb162f3b04f&currency=BTC&start=2020-06-12T00%3A00%3A00Z&end=2020-06-13T00%3A00%3A00Z"
    );

    data.forEach(d => {
      const rate = numeral(d.rate).format("0.00");
      const timestamp = moment(d.timestamp).format("MM/DD/YYYY");
      

      // const {
      //     rate = (d.rate).toFixed(2)
      //     // timestamp
      // } = d;

      this.arrRate.push({ rate, timestamp });
    });
    console.log(this.arrRate)

  }
};
</script>
<style>
</style>