<script>
import { Line } from "vue-chartjs";

export default {
  extends: Line,
  props: {
    label: {
      type: String
    },
    chartData: {
      type: Array
    },
    options: {
      type: Object
    },
    chartColors: {
      type: Object
    },
  },
  mounted() {
    const rates = this.chartData.map((d) => d.rate);
    const timestamps = this.chartData.map((d) => d.timestamp);

    const {
      borderColor,
      pointBorderColor,
      pointBackgroundColor,
      backgroundColor,
    } = this.chartColors;

    this.renderChart(
      {
        labels: timestamps,
        datasets: [
          {
            label: this.label,
            data: rates,
            borderColor: borderColor,
            pointBorderColor: pointBorderColor,
            pointBackgroundColor: pointBackgroundColor,
            backgroundColor: backgroundColor,
          },
        ],
      },
      this.options
    );
  },
};
</script>