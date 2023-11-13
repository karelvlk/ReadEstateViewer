const { Pool } = require("pg");

const initPool = (dbConfig) => {
  return new Pool(dbConfig);
};

const createTable = async (pool) => {
  const client = await pool.connect();
  try {
    const queryText = `
      CREATE TABLE IF NOT EXISTS images (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255),
        img_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `;
    await client.query(queryText);
  } finally {
    client.release();
  }
};

const insertData = async (pool, dataList) => {
  const client = await pool.connect();
  try {
    for (const data of dataList) {
      const queryText = "INSERT INTO images (title, img_url) VALUES ($1, $2)";
      const values = [data.title, data.imgUrl];
      await client.query(queryText, values);
    }
  } finally {
    client.release();
  }
};

const closePool = async (pool) => {
  await pool.end();
};

module.exports = {
  initPool,
  createTable,
  insertData,
  closePool,
};
