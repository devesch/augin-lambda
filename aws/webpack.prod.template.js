const path = require("path");

const {
    CleanWebpackPlugin
} = require("clean-webpack-plugin");

const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = {
    entry: "/src/js/index.js",
    mode: 'production',
    output: {
        path: path.resolve(__dirname, 'src/dist'),
        filename: 'js/index.js',
        publicPath: 'https://cdn.project_main_name/',
        libraryTarget: 'var',
        library: 'index'
    },
    plugins: [
        new CleanWebpackPlugin(),
        new MiniCssExtractPlugin({
            filename: "style/style.css"
        }),
    ],
    module: {
        rules: [{
                test: /\.s[ac]ss$/i,
                exclude: /node_modules/,
                use: [
                    MiniCssExtractPlugin.loader,
                    "css-loader",
                    "sass-loader",
                ]
            },
            {
                test: /\.(woff|woff2|eot|ttf|otf)$/i,
                exclude: /node_modules/,
                type: 'asset/resource',
                generator: {
                    filename: 'fonts/[name][ext]'
                }
            }
        ],
    },
}