const puppeteer = require("puppeteer");
const pg = require("./postgres");

const DEFAULT_URL = "https://www.sreality.cz/hledani/prodej/byty";
const PAGE_PREFIX = "?strana=";
const PAGE_SIZE = 20;
const SCRAPE_COUNT = 500;

const get_scrape_urls = () => {
  const urls = [];
  for (let i = 1; i < Math.ceil(SCRAPE_COUNT / PAGE_SIZE) + 1; i++) {
    urls.push(`${DEFAULT_URL}${PAGE_PREFIX}${i}`);
  }

  return urls;
};

const extract_title_and_img = async (page, prop) => {
  const titleElement = await prop.$("div > div > div > span > h2 > a > span");
  const title = await page.evaluate(
    (element) => element.textContent,
    titleElement
  );

  const imgElement = await prop.$("preact > div > div > a > img");
  const imgUrl = await page.evaluate((element) => element.src, imgElement);

  return { title, imgUrl };
};

const scrape_items = async () => {
  const browser = await puppeteer.launch({
    executablePath: "/usr/bin/chromium",
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });

  try {
    const urls = get_scrape_urls();

    let items = [];
    for (let u = 0; u < urls.length; u++) {
      const url = urls[u];
      const page = await browser.newPage();
      await page.goto(url);

      await page.waitForSelector(".dir-property-list");
      const propertyElements = await page.$$(".dir-property-list");

      let properties = [];
      for (const element of propertyElements) {
        await element.waitForSelector(".property");
        const propertyDivs = await element.$$(".property");
        for (const prop of propertyDivs) {
          const item = await extract_title_and_img(page, prop);
          properties.push(item);
        }
      }

      console.log(`Successfully scraped url ${u + 1}/${urls.length}`);

      items = [...items, ...properties];
    }
    return items;
  } catch (e) {
    throw Error(`Error occured while scraping items! ${e}`);
  } finally {
    await browser.close();
  }
};

const upload_scraped_data_to_db = async (dataList, dbConfig) => {
  try {
    const pool = pg.initPool(dbConfig);
    console.log("Postgres pool initialized");
    await pg.createTable(pool);
    await pg.insertData(pool, dataList);
    await pg.closePool(pool);
    console.log(`Scraped data successfully uploaded to db`);
  } catch (e) {
    throw Error(`Error occured while uploading scraped data to db! ${e}`);
  }
};

(async () => {
  const dbConfig = {
    user: "user1",
    host: "db",
    database: "sreality_db",
    password: "password1",
    port: 5432,
  };
  const scraped_items = await scrape_items();
  await upload_scraped_data_to_db(scraped_items, dbConfig);
})();
