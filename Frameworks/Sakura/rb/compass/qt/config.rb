# config.rb
# 8/8/2013 jichi
# Compass for Qt

# Set this to the root of your project when deployed:
http_path = '/'
css_dir = 'css'
sass_dir = 'sass'
images_dir = 'images'
javascripts_dir = 'js'

# Import sass QT extension

ROOT_DIR = '../../..'

def require_all(dir)
  Dir["#{dir}/*.rb"].each { |file| require_relative file }
end

require_all "#{ROOT_DIR}/rb/sass-qt"

# EOF
