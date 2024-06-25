# Frontend

Edit src/config.js

## Run local

```bash
npm install
npm start
```

## Build

```bash
npm run build
```

## Deploy

```bash
aws s3 sync ./build s3://$bucket_name
aws cloudfront create-invalidation --distribution-id $cloudfront_id --paths "/*"
echo $cloudfront_name
```

## Delete

```bash
aws s3 rm s3://$bucket_name --recursive

```
