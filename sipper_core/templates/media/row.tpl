<a id="{{ file_details.hash }}" class="data-row" href="{{ file_details.file_link }}">
    <div class="card" >
         <div class="icon">
             % if file_details.is_dir:
               <i class="fa fa-folder" aria-hidden="true"></i>
             % else:
               <i class="file icon-{{file_details.file_icon_style_class}}"></i>
             % end
         </div>
         <div class="details">
             <h2>{{file_details.file_name}}</h2>
             <p>Last Modified: {{file_details.last_modified_date}}</p>
             <p>Permissions: {{file_details.file_permissions}}</p>
             % if not file_details.is_dir:
               <p>Size: {{file_details.file_size}}</p>
             % end
         </div>
    </div>
</a>
