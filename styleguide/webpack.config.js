const path = require('path');

const ExtractTextPlugin = require('extract-text-webpack-plugin');

const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = [
  {
    name: 'styles',
    entry: path.join(__dirname, 'static/scss', 'styles.scss'),
    output: {
      path: path.join(__dirname, 'public/css'),
      filename: 'styles.css',
    },
    module: {
      loaders: [
        {
          test: /\.scss$/,
          use: ExtractTextPlugin.extract({
            fallback: 'style-loader',
            use: [
              { loader: 'css-loader',
                options: { sourceMap: true } },
              { loader: 'sass-loader',
                options: { sourceMap: true } },
            ],
          }),
        },
        {
          test: /\.(ttf|otf|eot|svg|woff(2)?)(\?[a-z0-9]+)?$/,
          loader: 'file-loader?name=font/[name].[ext]',
        },
      ],
    },
    plugins: [
      new ExtractTextPlugin('styles.css'),
      new CopyWebpackPlugin([
          {from:'../ui/static/img/', to:'../img'}
      ])
    ],
  },
];

if (process.env.USE_POLLING === 'true') {
  module.exports[0].watchOptions = {
    poll: true,
  };
}
