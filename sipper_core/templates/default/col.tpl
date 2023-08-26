<td class="{{col.style_class}}">
  % if col.is_link:
      % include(col.link_template_file, link=col.value)
    % elif col.is_itag:
      % include(col.itag_template_file, iTag=col.value)
    % else:
      {{col.value}}
  % end
</td>
