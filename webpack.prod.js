const path = require("path");
const json = require('./.vscode/enviroment_variables.json');
var cdn_val = "";


const {
    CleanWebpackPlugin
} = require("clean-webpack-plugin");

const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const TerserPlugin = require("terser-webpack-plugin");

module.exports = (env) => {

    var webpack_mode = "";
    var minimize_webpack = "";

    if (env.production) {
        cdn_val = `https://cdn.augin.app/`;
        webpack_mode = "production";
        minimize_webpack = true;
    } else {
        cdn_val = `https://cdn.augin.app/`;
        webpack_mode = "development";
        minimize_webpack = false;
    }

    return {
        entry: {
            index: "/src/js/index.js",
            utils: "/src/js/utils.js",
        },
        mode: webpack_mode,
        // mode: 'production',
        // mode: 'development',
        output: {
            path: path.resolve(__dirname, 'src/dist'),
            filename: 'js/[name].js',
            publicPath: cdn_val,
            libraryTarget: 'var',
            library: ['js', '[name]']
        },
        resolve: {
            modules: ['node_modules'],
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
                        {
                            loader: "sass-loader",
                            options: {
                                additionalData: "$cdn_val: " + "\"" + cdn_val + "\"" + ";"
                            },
                        }
                    ]
                },
                {
                    test: /\.(woff|woff2|eot|ttf|otf)$/i,
                    exclude: /node_modules/,
                    type: 'asset/resource',
                    generator: {
                        filename: 'assets/fonts/[name][ext]'
                    }
                }
            ],
        },
        optimization: {
            minimize: minimize_webpack,
            minimizer: [
                new CssMinimizerPlugin(),
                new TerserPlugin({
                    terserOptions: {
                        compress: {
                            drop_console: true,
                        }
                    }
                }),
            ],
        },
    };
};