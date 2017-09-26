# compass-qt/rescue.rb
# 3/25/2014 jichi
# Disable error checking
#require_relative 'config'

# Enable support qlineargradient
# https://groups.google.com/forum/#!msg/haml/fg9Pwzb20h4/UFAH3L2wcg4J
#
# See: sass/script/lexer.rb
module Sass::Script
  class Lexer
    alias sass_special_fun special_fun
    def special_fun # @override
      return if sass_special_fun
      #return unless str1 = scan(/((-[\w-]+-)?qlineargradient:[a-z\.]*)\(/i)
      return unless str1 = scan(/((-[\w-]+-)?qlineargradient|expression:[a-z\.]*)\(/i)
      dprint 'unparsing qlineargradient'
      str2, _ = Sass::Shared.balance(@scanner, ?(, ?), 1)
      c = str2.count("\n")
      old_line = @line
      old_offset = @offset
      @line += c
      @offset = (c == 0 ? @offset + str2.size : str2[/\n(.*)/, 1].size)
      [:special_fun,
        Sass::Util.merge_adjacent_strings(
          [str1] + Sass::Engine.parse_interp(str2, old_line, old_offset, @options)),
        str1.size + str2.size]
    end
  end
end

# EOF
