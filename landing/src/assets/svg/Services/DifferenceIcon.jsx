import * as React from "react";

function SvgComponent(props) {
  return (
    // <svg xmlns="http://www.w3.org/2000/svg" width={39.581} height={39.58} viewBox="0 0 39.581 39.58" {...props}>
    <svg xmlns="http://www.w3.org/2000/svg" height={"40"} viewBox="0 -960 960 960" width={"40"} fill="#580cd2" {...props}>
    <path d="M493.33-524H560v-82.67h82.67v-66.66H560V-756h-66.67v82.67h-82.66v66.66h82.66V-524Zm-82.66 157.33h232v-66.66h-232v66.66ZM280-173.33q-27 0-46.83-19.84Q213.33-213 213.33-240v-613.33q0-27 19.84-46.84Q253-920 280-920h325.33L840-685.33V-240q0 27-19.83 46.83-19.84 19.84-46.84 19.84H280Zm0-66.67h493.33v-414.67L572-853.33H280V-240ZM146.67-40q-27 0-46.84-19.83Q80-79.67 80-106.67V-706h66.67v599.33h478.66V-40H146.67ZM280-240v-613.33V-240Z"/>
    </svg>
  );
}

export default SvgComponent;
