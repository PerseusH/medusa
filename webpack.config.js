//__dirname是node.js中的一个全局变量，它指向当前执行脚本所在的目录

var webpack = require('webpack');

module.exports = {//注意这里是exports不是export/////////
    devtool: 'eval-source-map',
    entry: [
        'webpack/hot/dev-server',
        __dirname + '/react/test.js'],//唯一入口文件，就像Java中的main方法
    output: {//输出目录
        path: __dirname + "/static",//打包后的js文件存放的地方
        filename: "app.js"//打包后的js文件名
    },
    module: {
        loaders: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                loader: 'babel-loader'
            }, {
                test:/\.css$/,
                loader: 'style-loader!css-loader'
            }, {
                test:/\.less$/,
                loader: 'style-loader!css-loader!less-loader'
            }, {
                test:/\.(png|jpg|svg|gif)$/,
                loader: 'url-loader?limit=25000'
            }
        ]
    },

    plugins: [
        new webpack.HotModuleReplacementPlugin() //热模块替换HMR插件
    ],

    //webpack-dev-server
    devServer: {
        contentBase: './static', //默认webpack-dev-server会为根文件夹提供本地服务器，如果想为另外一个目录下的文件提供本地服务器，应该在这里设置其所在目录
        // colors: false, //是否在cmd终端中输出彩色日志
        historyApiFallback: true, //Html5 API
        inline: true, //设置为true，当源文件改变时会自动刷新页面
        port: 8010, //设置默认监听端口，如果省略，默认为"8080"
        progress: true //显示合并代码进度
    }
};
