# Traveling Santa solution verification program in R language

R_EARTH <-  6378L
FILENAME <-  'nicelist.txt'
FILE_TO_VERIFY <-  'output.txt'
# --------------------------------------------------------------------------
to_xyz <- function(data) {

   phi <- data$LAT * pi / 180
   ksi <- data$LONG * pi / 180
   
   x <- cos(phi) * cos(ksi)
   y <- cos(phi) * sin(ksi)
   z <- sin(phi)
   
   return(data.frame(X = x, Y = y, Z = z))
}
# --------------------------------------------------------------------------
x_prod <- function(a, b) {
   r <-
      c(a[2L] * b[3L] - a[3L] * b[2L], -(a[1L] * b[3L] - a[3L] * b[1L]),
        a[1L] * b[2L] - a[2L] * b[1L])
   return(r)
}

# --------------------------------------------------------------------------
c_prod <- function(a, b) {
   r <- a[1L] * b[1L] + a[2L] * b[2L] + a[3L] * b[3L]
   return(r)
}
# --------------------------------------------------------------------------
normf <- function(a) {
   return(sqrt(sum(a ^ 2)))
}

# --------------------------------------------------------------------------
distance <- function(u, v) {
   a <- c(u$X, u$Y, u$Z)
   b <- c(v$X, v$Y, v$Z)
   d <- R_EARTH * atan2(normf(x_prod(a, b)), c_prod(a, b))
   return(d)
}
# --------------------------------------------------------------------------
read_solution_file <- function() {
   cat('Reading solution file...')
   f <- file(FILE_TO_VERIFY, 'r', encoding = 'UTF-8')
   #fields <- count.fields(f, sep = ';')
   lines <- readLines(f, encoding = 'UTF-8')
   close(f)
   
   cat('Converting text lines to integers...\n')
   solution <- vector('list', length(lines))
   i <- 1L
   for (item  in lines) {
      tmp <- stringr::str_split(item, ';')[[1L]]
      solution[[i]] <- type.convert(tmp)
      i <- i + 1L
   }
   return(solution)
}
# --------------------------------------------------------------------------
calculate_total_distance <- function(home, children, solution) {
   cat('Calculating the total distance: ')
   tally <- 0
   id <- c()
   for (s in solution) {
      t <- distance(home, children[s[1L] - 1L,])
      
      len <- length(s)
      if (len > 1L) {
         for (i in 1L:(len - 1L)) {
            a <- children[s[i] - 1L,]
            b <- children[s[i + 1L] - 1L,]
            t <- t + distance(a, b)
         }
      }
      t <- t + distance(home, children[s[len] - 1L,])
      
      tally <- tally + t
      
      for (i in 1L:len) {
         id <- c(id, children[s[i] - 1L, 1L])
         
      }
   }
   cat(tally, 'km\n')
   
   cat('#ID:', length(id), ' ')
   cat('All IDs unique? ')
   if (isTRUE(all.equal(id, unique(id)))) {
      cat('True')
   }
   else {
      cat('False')
   }
   cat('\n')
   return(tally)
}
# --------------------------------------------------------------------------
parallel_do <- function(x, home, children, solution) {
   
   return(calculate_total_distance(home, children, solution[x]))   
}
# ------------------------- "main" (global) ---------------------------------
home <- data.frame(
   ID = 1L,
   LAT = 68.073611,
   LONG = 29.315278,
   WEIGHT = 0L
)

cat('Reading input file...\n')
children <-
   read.csv2(
      FILENAME,
      FALSE,
      dec = '.',
      col.names = c('ID', 'LAT', 'LONG', 'WEIGHT'),
      colClasses = c('integer', 'numeric', 'numeric', 'integer')
   )

# Add columns of x,y,z
tmp <- to_xyz(children)
children <- cbind(children, tmp)

tmp <- to_xyz(home)
home <- cbind(home, tmp)
remove(tmp)

solution <- read_solution_file()
t <- calculate_total_distance(home, children, solution)
# --------------------------------------------------------------------------
# Parallel calculation
n_cores <- 2L
cat('Calculating the total distance in parallel: ')
cl <-
   parallel::makeCluster(c(rep('localhost', n_cores)),
                         type = 'PSOCK',
                         nnodes  = n_cores)
# export all variables / symbols
parallel::clusterExport(cl, objects())
sp <-
   parallel::clusterSplit(cl, seq = seq.int(1L, length(solution), by = 1L))
res <-
   parallel::clusterApply(cl, fun = parallel_do, x = sp, home, children, solution)
parallel::stopCluster(cl)
t2 <- do.call(sum, res)
# identical() gives FALSE, slight difference in the last decimal(s)
cat(t2, 'km. Matches the single-threaded calculation? ',
    isTRUE(all.equal(t, t2)),'\n')

