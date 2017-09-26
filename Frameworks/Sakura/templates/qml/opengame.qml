{# opengame.qml 11/28/2012 jichi
 # @param  path  unicode not None  The path to the executable.
 # @param  launchPath  unicode not None  The path to the game launcher executable.
-#}
import org.sakuradite.reader 1.0 as Plugin
Plugin.GameManagerProxy {
  function run() {
    openLocation("{{path}}", "{{launchPath}}")
  }
}
