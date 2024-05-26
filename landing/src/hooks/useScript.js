import { useEffect } from 'react';

// create useScript hook which will take url and env as arguments. env by default is NaN
// useEffect will run only if the process.env.REACT_APP_ENV is equal to env
const useScript = (url, env = NaN) => {
    useEffect(() => {
        console.debug('useScript: url:', url, 'env:', env, 'process.env.REACT_APP_ENV:', process.env.REACT_APP_ENV);
        // if process.env.REACT_APP_ENV is equal to env or env is NaN then only run the useEffect
        if (process.env.REACT_APP_ENV === env || isNaN(env)) {
            const script = document.createElement('script');

            script.src = url;
            script.async = true;

            document.body.appendChild(script);

            return () => {
                document.body.removeChild(script);
            }
        }
    }, [url, env]);
};


// const useScript = (url, env=NaN) => {
//   useEffect(() => {
//     if (process.env.REACT_APP_ENV === env) {
//         const script = document.createElement('script');

//         script.src = url;
//         script.async = true;

//         document.body.appendChild(script);

//         return () => {
//         document.body.removeChild(script);
//         }
//     }
//   }, [url]);
// };

export default useScript;
