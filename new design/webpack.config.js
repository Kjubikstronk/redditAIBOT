const path = require("path")

module.exports = {
  entry: "./src/index.tsx",
  output: {
    path: path.resolve(__dirname, "static/js"),
    filename: "dashboard-bundle.js",
    clean: true,
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: "ts-loader",
        exclude: /node_modules/,
      },
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"],
      },
    ],
  },
  resolve: {
    extensions: [".tsx", ".ts", ".js"],
  },
  externals: {
    react: "React",
    "react-dom": "ReactDOM",
  },
  optimization: {
    minimize: true,
  },
  devtool: "source-map",
}
