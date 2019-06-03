<html>
    <head>
    </head>

    <body>

<?

tableList = self.db.GetTableList()
self.write("%s tables<br/>" % len(tableList))

?>
    <table>
        <tr><th>table</th><th>count</th></tr>

<?

for table in tableList:
    t = self.db.GetTable(table)
    self.write("<tr><th>%s</th><th>%s</th></tr>" % (table, Commas(t.Count())))

?>

    </table>
    </body>
</html>
