import fetch from 'node-fetch'

const defaultVersion = '0.0.0'
const packageNames = process.argv.slice(2, process.argv.length)
const api = (packageName) => `https://pypi.org/pypi/${packageName}/json`

Promise.all(
  packageNames.map((packageName) =>
    fetch(api(packageName))
      .then((response) => response.json())
      .then((response) => response.info.version)
      .catch((err) => defaultVersion)
      .then((version) => ({
        name: packageName,
        version,
      }))
  )
)
  .then((versions) => {
    const versionsObj = Object.create({})
    versions.forEach((version) => (versionsObj[version.name] = version.version))
    return versionsObj
  })
  .then((versions) => JSON.stringify(versions))
  .then((versions) => process.stdout.write(versions))
