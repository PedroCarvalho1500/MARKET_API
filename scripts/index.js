

const API_BASE_URL = 'https://market-api-g8lp.onrender.com/';

//const API_BASE_URL = 'http://localhost:8000/';

const instance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});


export const fetchData = async () => {
  try {
    const response = await instance.get('/markets');
    return response.data;
  } catch (error) {
    console.error('Error fetching data: ', error);
    
    throw error;
  }
};


const markets = await fetchData();

console.log(markets);