import { useEffect } from 'react';

// create useScript hook which will take url and env as arguments. env by default is NaN
// useEffect will run only if the process.env.REACT_APP_ENV is equal to env
const useScript = (url, env = NaN) => {
    useEffect(() => {
        // if process.env.REACT_APP_ENV is equal to env or env is NaN then only run the useEffect
        if (Number.isNaN(env) || process.env.REACT_APP_ENV === env) {
            // console.info('useScript: loading url:', url, 'env:', env, 'process.env.REACT_APP_ENV:', process.env.REACT_APP_ENV, 'isNaN(prod):' , isNaN('prod'));
            const script = document.createElement('script');

            script.src = url;
            script.async = true;

            document.body.appendChild(script);

            return () => {
                document.body.removeChild(script);
            }
        } else
        {
            console.debug('useScript: skipping url:', url, 'required env:', env, 'process.env.REACT_APP_ENV:', process.env.REACT_APP_ENV);
        }
    }, [url, env]);
};

export default useScript;
